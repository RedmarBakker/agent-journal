"""Reads the command corpus scripts/corpus_commands.py writes and gives each line an ID kept beside it; splits every line with the journal's own Chain into single commands, its parts, each with an ID of its own (a line of one part is its own part); and writes beside the corpus how each line's parts are joined (chains.jsonl), one JSON file per program of its subcommands, options, value kinds and forms, each form with how often it was seen and a few of its parts (forms/), every distinct value scrubbed with an ID kept across runs (values.jsonl), and the lines the splitter may have split wrongly, by the check that found them (splitter-report.txt). A part's text is its line split again with pieces(staged(Chain.chained(line))). Run from the repository: PYTHONPATH=src python3 -m scripts.corpus_forms <corpus>."""

import json
import multiprocessing
import os
import re
import secrets
import shlex
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from functools import lru_cache, partial
from pathlib import Path
from typing import Iterator, TextIO

from journal.support.chain import Chain
from journal.support.command_shape import LOOP_PATTERN as LOOP_START, CommandShape
from journal.support.part import Part
from scripts.corpus_commands import anonymised

# lowercase letters and digits without the look-alikes 0, 1, l and o
ID_ALPHABET = "23456789abcdefghijkmnpqrstuvwxyz"
ID_GROUPS = 4
ID_GROUP_LENGTH = 4
ID_PATTERN = rf"(?:[{ID_ALPHABET}]{{{ID_GROUP_LENGTH}}}-){{{ID_GROUPS - 1}}}[{ID_ALPHABET}]{{{ID_GROUP_LENGTH}}}"
LINE_ID = re.compile(rf"^({ID_PATTERN})\t")
PART_ID = re.compile(ID_PATTERN)
# a list of IDs, written on one line in a JSON file indented otherwise
SAMPLE_IDS = 5
ID_LIST = re.compile(rf'\[\s+("{ID_PATTERN}"(?:,\s+"{ID_PATTERN}")*)\s+\]')
PROGRAM_NAME = re.compile(r"[A-Za-z_][\w.+-]*")
PUNCTUATION = ";&|()<>\n"
# a punctuation character inside quotes or escaped is part of a word: it stands in a private character while shlex reads
PROTECTED = {character: chr(0xE000 + index) for index, character in enumerate(PUNCTUATION + "#")}
PROTECT = str.maketrans(PROTECTED)
UNPROTECT = str.maketrans({stand_in: character for character, stand_in in PROTECTED.items()})
QUOTED_OR_ESCAPED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"|\\.", re.S)
# a command substitution, $(...), `...` or <(...), stands in this word, read as the kind substitution
SUBSTITUTION = "\ue020"
SUBSTITUTION_START = re.compile(r"\$\(|<\(|>\(")
BACKTICKS = re.compile(r"`[^`]*`")
HEREDOC = re.compile(r"(?<!<)<<-?\s*(['\"]?)([\w.-]+)\1")
OPERATOR = re.compile(r"&&|\|\||;;|\|&|>>|<<<|<<|>&|<&|&>>|&>|[|;&()<>\n]")
REDIRECTS = {">", ">>", "<", "<<", "<<<", ">&", "<&", "&>", "&>>"}
# a redirect that names a file descriptor, 2>&1, rather than a file
DESCRIPTOR_REDIRECTS = {">&", "<&"}
HEREDOC_MARK = "<< heredoc"
SEPARATORS = {";", "\n", "&&", "&"}
# a newline joins two commands as a ; does, and so does the end of a heredoc's body
JOINS = {"\n": ";", "": ";"}
PIPES = ("||", "|&", "|")
PIPE_STAGES = {"|", "|&"}
SUBSHELL_OPEN = "("
SUBSHELL_CLOSE = ")"
# the shell's own words in front of a command, which no command is known by
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "time", "{", "}", "done", "fi", "esac", "command", "sudo", "builtin"}
HEADERS = {"for", "case", "select", "function"}
# the words that open and close a compound command, which the splitter keeps as one part
OPENERS = {"for", "while", "until", "if", "case", "select", "{"}
CLOSERS = {"done", "fi", "esac", "}"}
# the words that lead the commands of a compound command's body, after which the command itself starts
LEADING_KEYWORDS = {"do", "then", "else", "elif", "!", "time"}
# words a part never starts with, since each only ends or continues a command before it
NO_PROGRAM = {")", "fi", "done", "esac", "then", "do", "else", "elif", "}", ";;", "in"}
NO_PROGRAM_START = set("-=)]},")
# a program named in quotes, "$C" --headless, a whole word
QUOTED_PROGRAM = re.compile(r"""(?:"(?:\\.|[^"\\])*"|'[^']*')(?:\s|$)""")
OPERATOR_STARTS = ("&&", "||", "|", ";", "&", ">", "<")
QUOTES = "'\"`"
SIGNIFICANT = re.compile(r"\\.|['\"`()|#]", re.S)
# the characters a comment starts after
COMMENT_STARTS = " \t\n;&|("
ASSIGNMENT = re.compile(r"[A-Za-z_]\w*=")
SUBCOMMAND = re.compile(r"[a-z][a-z0-9_-]{0,29}")
SUBCOMMAND_DEPTH = 3
# a level of subcommands: most parts name a word there, from a small vocabulary, each word seen in a few parts
SUBCOMMAND_SHARE = 0.75
SUBCOMMAND_VOCABULARY = 0.1
SUBCOMMAND_VOCABULARY_FLOOR = 5
SUBCOMMAND_PARTS = 3
LONG_OPTION = re.compile(r"(--[A-Za-z][\w-]*)=(.*)", re.S)
OPTION = re.compile(r"--?[A-Za-z][\w-]*")
ATTACHED_VALUE = re.compile(r"(-[A-Za-z])(\d.*)", re.S)
NUMBER_OPTION = re.compile(r"-\d+")
OPTIONS_END = "--"
# an option takes a value when it is never last nor followed by an option, its next word mostly of one kind
VALUE_OCCURRENCES = 3
VALUE_INTERRUPTIONS = 0.02
VALUE_KIND_SHARE = 0.6
# kinds an option's value may vary between, counted as one when judging whether it takes a value: a commit message is text or code
KIND_FAMILIES = {"code": "prose", "text": "prose", "string": "prose", "word": "name", "branch": "name", "revision": "name"}
LAST = "last"
NEXT_OPTION = "option"
FLAG = "flag"
# the subcommand path of a program run with none, as git -C repo is
NO_SUBCOMMAND = "(no subcommand)"
# a word such as -Schevron is -S with its value attached when -S is seen so with at least this many values, the whole word fewer times than ATTACHED_WORD
ATTACHED_VALUES = 2
ATTACHED_WORD = 3
SHORT_OPTION = re.compile(r"-[A-Za-z]")
SHORT_ATTACHED = re.compile(r"(-[A-Za-z])(.+)", re.S)
# a program has many parts from this many on, where a form seen once is suspect
LONE_FORM_PARTS = 100
BASH_CHUNK = 2000
BASH_TIMEOUT = 60
RECURRING = 2
BRANCH_WORDS = {"main", "master", "development", "develop", "trunk"}
# each kind a value may be, in the order a value is tried against them
KINDS = (
    ("substitution", re.compile(rf".*{SUBSTITUTION}.*", re.S)),
    ("variable", re.compile(r"\$\{?[A-Za-z_]\w*\}?|\$\d")),
    ("number", re.compile(r"-?\d+(?:\.\d+)?")),
    ("duration", re.compile(r"\d+(?:\.\d+)?(?:ms|s|m|h|d)")),
    ("date", re.compile(r"\d{4}-\d{2}-\d{2}(?:[T ][\d:.]+Z?)?|\d{1,2}:\d{2}(?::\d{2})?|\d+[. ](?:seconds?|minutes?|hours?|days?|weeks?|months?|years?)[. ]ago|yesterday|today|now")),
    ("version", re.compile(r"v?\d+(?:\.\d+){1,3}(?:[-+][\w.]+)?")),
    ("number range", re.compile(r"\d+(?:,(?:\d+|\$))?[pd]|\d+[,-](?:\d+|\$)?")),
    ("revision", re.compile(r"HEAD(?:[~^]\d*)*|@\{\w+\}|(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}")),
    ("range", re.compile(r"(?!.*\.\./)(?!.*/\.\.)[\w^~@{}][\w./^~@{}-]*?\.\.\.?[\w./^~@{}-]*")),
    ("branch", re.compile(r"(?:origin|upstream)/[\w./-]+|(?:worker|feature|fix|hotfix|release)/[\w./-]+|" + "|".join(sorted(BRANCH_WORDS)))),
    ("url", re.compile(r"[a-z][\w+.-]*://\S*")),
    ("test name", re.compile(r"[\w./-]+::[\w:\[\].-]+")),
    ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("address", re.compile(r"[\w.-]+:\d{2,5}(?:/\S*)?")),
    ("json", re.compile(r"[\[{].*[:,].*[\]}]", re.S)),
    ("assignment", re.compile(r"[A-Za-z_]\w*=.*", re.S)),
    ("pattern", re.compile(r".*(?:\\[|()bswdS<>]|\.\*|\.\+).*|\^.*|.*[^\\]\$", re.S)),
    ("code", re.compile(r""".*(?:\bimport\s|\bdef\s|\bclass\s\w|\bfunction\b|=>|\bconst\s|\breturn\b|print\(|console\.|\w\.\w+\(|\w\s*=\s*[\w'"\[({]|[{}]).*""", re.S)),
    ("text", re.compile(r".*\s.*", re.S)),
    ("stdin", re.compile(r"-")),
    ("glob", re.compile(r".*[*?].*")),
    ("pattern", re.compile(r".*(?:\\[|.wdsbS()+?]|[\^$\[\]|()+]).*")),
    ("path", re.compile(r".*/.*|~.*|\..*")),
    ("file", re.compile(r"[\w-]+(?:\.[\w-]+)*\.[A-Za-z]\w{0,5}")),
    ("word", re.compile(r"[A-Za-z_][\w-]*")),
    ("empty", re.compile(r"")),
)
FALLBACK_KIND = "string"


def new_id(taken: set[str]) -> str:
    while (found := random_id()) in taken:
        pass
    taken.add(found)
    return found


# 80 random bits, five a letter, in groups joined by a dash: 3kq9-x7mb-...
def random_id() -> str:
    bits = int.from_bytes(secrets.token_bytes(ID_GROUPS * ID_GROUP_LENGTH * 5 // 8))
    letters = "".join(ID_ALPHABET[(bits >> (5 * index)) & 31] for index in range(ID_GROUPS * ID_GROUP_LENGTH))
    return "-".join(letters[index:index + ID_GROUP_LENGTH] for index in range(0, len(letters), ID_GROUP_LENGTH))


# the corpus's lines read one by one, each by its ID, a line without one given a new one, copied with its ID into the copy
def identified(corpus: Path, copy: TextIO, taken: set[str], fresh: list[str]) -> Iterator[tuple[str, str]]:
    with corpus.open(errors="replace") as lines:
        for raw in lines:
            raw = raw.rstrip("\n")
            found = LINE_ID.match(raw)
            kept = bool(found) and found.group(1) not in taken
            line_id = found.group(1) if kept else new_id(taken)
            taken.add(line_id)
            fresh += [] if kept or not raw else [line_id]
            copy.write(f"{line_id}\t{raw[found.end():] if found else raw}\n" if raw else "\n")
            if raw:
                yield line_id, raw[found.end():] if found else raw


# a line's parts and the operators between them, as the journal's Chain splits it and a subshell, a pipe and a || inside a part split it further
def pieces(staged: list[tuple[str, list[tuple[str, str]]]]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for separator, stages in staged:
        found += [("operator", JOINS.get(separator, separator))] if found else []
        for operator, segment in stages:
            found += [("operator", operator)] if operator else []
            found += subshell(segment)
    return found


# each part the splitter gives with the stages of its pipeline
def staged(chained: list[tuple[str, str]]) -> list[tuple[str, list[tuple[str, str]]]]:
    return [(separator, pipeline(part)) for separator, part in chained]


def subshell(segment: str) -> list[tuple[str, str]]:
    if Part(segment).is_subshell():
        return [("operator", SUBSHELL_OPEN), *pieces(staged(Chain.chained(segment[1:-1].strip()))), ("operator", SUBSHELL_CLOSE)]
    return [("part", segment)]


# a part's commands at its pipes and its ||, quotes, escapes and brackets respected, a heredoc's body kept with the command it feeds; a loop, a branch or a group stays whole
def pipeline(part: str) -> list[tuple[str, str]]:
    if LOOP_START.match(part) or part.startswith("{"):
        return [("", part)]
    heredoc = HEREDOC.search(part)
    body_start = part.find("\n", heredoc.end()) if heredoc else -1
    if body_start < 0:
        return piped(part)
    found = piped(part[:body_start])
    fed = next((index for index, (_, segment) in enumerate(found) if HEREDOC.search(segment)), len(found) - 1)
    return [(operator, segment + part[body_start:] if index == fed else segment) for index, (operator, segment) in enumerate(found)]


def piped(part: str) -> list[tuple[str, str]]:
    found, operator, start, passed = [], "", 0, -1
    for index, character, quote, depth in marks(part):
        if character != "|" or quote or depth or index <= passed:
            continue
        pipe = next(symbol for symbol in PIPES if part.startswith(symbol, index))
        passed = index + len(pipe) - 1
        if part[start:index].strip():
            found, operator, start = [*found, (operator, part[start:index].strip())], pipe, index + len(pipe)
    return [*found, (operator, part[start:].strip())] if part[start:].strip() else found


# each character of a text that opens or closes a quote or a bracket, or pipes, with the quote open and the bracket depth after it; escapes and comments passed over
def marks(text: str) -> Iterator[tuple[int, str, str, int]]:
    quote, depth, position = "", 0, 0
    while found := SIGNIFICANT.search(text, position):
        character, position = found.group(), found.end()
        if not quote and character == "#" and (found.start() == 0 or text[found.start() - 1] in COMMENT_STARTS):
            end = text.find("\n", position)
            position = len(text) if end < 0 else end
            continue
        if quote:
            quote = "" if character[-1] == quote and (quote == "'" or len(character) == 1) else quote
        elif character[0] != "\\":
            quote = character if character in QUOTES else ""
            depth += {"(": 1, ")": -1}.get(character, 0)
        yield found.start(), character, quote, depth


# why the splitter may have split a line wrongly, each reason named by the check that found it; none for a line it split well
def splitter_faults(text: str, chained: list[tuple[str, str]], stages: list[tuple[str, list[tuple[str, str]]]]) -> list[str]:
    faults = [fault for number, (_, part) in enumerate(chained, 1) for fault in part_faults(number, part)]
    joined = "".join(("" if separator == "&" else separator) + part for separator, part in chained)
    faults += [] if re.sub(r"\s+", "", joined.replace("\\\n", "")) == re.sub(r"(?<!\\);$", "", re.sub(r"\s+", "", text.replace("\\\n", ""))) else ["joined: its parts joined with their operators are not the line"]
    commands = sum(1 + sum(operator == "||" for operator, _ in pipeline) for _, pipeline in stages)
    pipes = sum(operator in PIPE_STAGES for _, pipeline in stages for operator, _ in pipeline)
    read = shlex_counts(text)
    faults += [f"shlex: shlex reads {read[0]} commands where the splitter reads {commands}, pipes aside"] if read and read[0] != commands else []
    faults += [f"pipes: shlex reads {read[1]} pipes where the splitter reads {pipes}"] if read and read[0] == commands and read[1] != pipes else []
    return faults


def part_faults(number: int, part: str) -> list[str]:
    first = part.split()[0] if part.split() else ""
    faults = [f"part start: part {number} starts with an operator"] if part.startswith(OPERATOR_STARTS) else []
    faults += [f"part start: part {number} starts with a quote that does not close its first word"] if part[:1] in QUOTES and not QUOTED_PROGRAM.match(part) else []
    faults += [f"part start: part {number} starts with {first}, which is no program"] if first in NO_PROGRAM or first[:1] in NO_PROGRAM_START else []
    opened = open_at_end(part)
    return faults + ([f"open at end: part {number} ends inside an open {opened}"] if opened else [])


def open_at_end(part: str) -> str:
    quote, depth = "", 0
    for _, _, quote, depth in marks(without_heredocs(part)):
        pass
    heredoc = HEREDOC.search(part)
    if quote:
        return "quote"
    if depth > 0:
        return "bracket"
    return "heredoc" if heredoc and not re.search(rf"\n\s*{re.escape(heredoc.group(2))}\s*(?:\n|$)", part[heredoc.end():]) else ""


# the commands shlex reads in a line at &&, ||, ; and &, and the pipes between them, outside a compound command or a subshell; none when
# shlex cannot read it
def shlex_counts(text: str) -> tuple[int, int] | None:
    try:
        found = tokens(text)
    except ValueError:
        return None
    count, pipes, open_command, piped, depth, compound = 0, 0, False, False, 0, 0
    for token in found:
        if is_operator(token):
            for operator in OPERATOR.findall(token):
                starts = operator == "(" and not (open_command or piped or depth or compound)
                count += 1 if starts else 0
                piped = operator in PIPE_STAGES and (open_command or piped)
                pipes += 1 if piped and not (depth or compound) else 0
                open_command = (open_command or starts) and operator not in SEPARATORS | PIPE_STAGES | {";;", "||"}
                depth = max(depth + {"(": 1, ")": -1}.get(operator, 0), 0)
            continue
        if not open_command and token in LEADING_KEYWORDS:
            continue
        count += 0 if open_command or piped or depth or compound else 1
        compound += 0 if open_command else 1 if token in OPENERS else -1 if token in CLOSERS else 0
        open_command, piped = True, False
    return count, pipes


def substituted(text: str) -> str:
    text = BACKTICKS.sub(SUBSTITUTION, text)
    while start := SUBSTITUTION_START.search(text):
        depth, index = 1, start.end()
        while index < len(text) and depth:
            depth += {"(": 1, ")": -1}.get(text[index], 0)
            index += 1
        text = text[:start.start()] + SUBSTITUTION + text[index:]
    return text


def without_heredocs(text: str) -> str:
    kept, ending = [], ""
    for row in text.split("\n"):
        if ending:
            ending = "" if row.strip() == ending else ending
            continue
        found = HEREDOC.search(row)
        ending = found.group(2) if found else ""
        kept.append(row)
    return "\n".join(kept)


def tokens(text: str) -> list[str]:
    protected = QUOTED_OR_ESCAPED.sub(lambda quoted: quoted.group(0).translate(PROTECT), substituted(without_heredocs(text)))
    lexer = shlex.shlex(protected, posix=True, punctuation_chars=PUNCTUATION)
    lexer.whitespace, lexer.whitespace_split, lexer.commenters = " \t\r", True, ""
    return list(lexer)


def is_operator(token: str) -> bool:
    return bool(token) and all(character in PUNCTUATION for character in token)


# the commands shlex reads in a part, each its words, and the part's redirects as written without their targets: 2>&1, >, << heredoc
def commands(part: str) -> tuple[list[list[str]], list[str]]:
    found, words, redirects, pending, comment = [], [], [], "", False
    for token in tokens(part):
        if not is_operator(token):
            comment = comment or token.startswith("#")
            redirects += [redirect(pending, token)] if pending else []
            words = words if pending or comment else [*words, token.translate(UNPROTECT)]
            pending = ""
            continue
        for operator in OPERATOR.findall(token):
            descriptor = words[-1] if operator in REDIRECTS and words and words[-1].isdigit() else ""
            words = words[:-1] if descriptor else words
            pending = descriptor + operator if operator in REDIRECTS else ""
            comment = comment and operator != "\n"
            if operator not in REDIRECTS:
                found, words = [*found, words], []
    return [bare for words in [*found, words] if (bare := stripped(words))], redirects


def redirect(operator: str, target: str) -> str:
    if operator.endswith("<<"):
        return HEREDOC_MARK
    return operator + target if operator[-2:] in DESCRIPTOR_REDIRECTS and (target.isdigit() or target == "-") else operator


# a command's words past the shell's keywords, its variables and the wrappers that only limit or set its run
def stripped(words: list[str]) -> list[str]:
    while words:
        if words[0] in HEADERS:
            return []
        if words[0] in KEYWORDS or ASSIGNMENT.match(words[0]):
            words = words[1:]
        elif words[0] in {"timeout", "gtimeout"} and len(words) > 1:
            words = words[2:]
        elif words[0] == "nice" and words[1:2] == ["-n"]:
            words = words[3:]
        elif words[0] == "env" and len(words) > 1 and (ASSIGNMENT.match(words[1]) or words[1] in {"-i", "-u"}):
            words = [words[0], *words[3 if words[1] == "-u" else 2:]]
        elif words[0] == "perl" and len(words) > 2 and "exec @ARGV" in words[2]:
            words = words[3:]
        else:
            return words
    return words


# a command's program, found past what only starts it as CommandShape does and past git's own options, and the words after it: uv run
# pytest -q is pytest, [-q]; git -C repo log is git, [log]
def program_run(words: list[str]) -> tuple[str, list[str]]:
    start = CommandShape.program_index(words)
    led = Part.leads(words[start if start < len(words) else 0:]) or words
    name = led[0].rsplit("/", 1)[-1]
    return (name if PROGRAM_NAME.fullmatch(name) else f"({kind(name)})"), led[1:]


# a line read in full: its pieces, each part with its runs and its redirects, and the splitter's faults on it
def read_line(entry: tuple[str, str]) -> tuple[str, list[tuple], list[str]]:
    line_id, line = entry
    text = line.replace("\\n", "\n")
    chained = Chain.chained(text)
    stages = staged(chained)
    return line_id, [piece if piece[0] == "operator" else read_part(piece[1]) for piece in pieces(stages)], splitter_faults(text, chained, stages)


def read_part(text: str) -> tuple:
    try:
        found, redirects = commands(text)
    except ValueError:
        return "part", text, [], [], False
    return "part", text, [program_run(words) for words in found], redirects, True


@lru_cache(maxsize=None)
def kind(value: str) -> str:
    return next((name for name, pattern in KINDS if pattern.fullmatch(value)), FALLBACK_KIND)


def option_parts(word: str) -> tuple[str, str | None] | None:
    if found := LONG_OPTION.fullmatch(word):
        return found.group(1), found.group(2)
    if found := ATTACHED_VALUE.fullmatch(word):
        return found.group(1), found.group(2)
    if NUMBER_OPTION.fullmatch(word):
        return "-<number>", None
    return (word, None) if OPTION.fullmatch(word) else None


# the words after a command's name split into its subcommand path, as journal message read 12 is message read, and the rest
def subcommand_paths(rests: list[list[str]], depth: int = 0) -> list[tuple[tuple[str, ...], list[str]]]:
    words = subcommand_words(rests, depth)
    deeper = {word: iter(subcommand_paths([rest[1:] for rest in rests if rest and rest[0] == word], depth + 1)) for word in words}
    return [prefixed(rest[0], next(deeper[rest[0]])) if rest and rest[0] in words else ((), rest) for rest in rests]


def subcommand_words(rests: list[list[str]], depth: int) -> set[str]:
    named = Counter(rest[0] for rest in rests if rest and SUBCOMMAND.fullmatch(rest[0]) and kind(rest[0]) == "word")
    total = sum(named.values())
    is_level = depth < SUBCOMMAND_DEPTH and bool(rests) and total >= SUBCOMMAND_SHARE * len(rests) and len(named) <= max(SUBCOMMAND_VOCABULARY_FLOOR, SUBCOMMAND_VOCABULARY * total)
    return {word for word, count in named.items() if count >= SUBCOMMAND_PARTS} if is_level else set()


def prefixed(word: str, entry: tuple[tuple[str, ...], list[str]]) -> tuple[tuple[str, ...], list[str]]:
    path, tail = entry
    return (word, *path), tail


def option_uses(rests: list[list[str]]) -> dict[str, Counter]:
    uses: dict[str, Counter] = defaultdict(Counter)
    for rest in rests:
        for index, word in enumerate(rest):
            if word == OPTIONS_END:
                break
            parts = option_parts(word)
            if parts:
                uses[parts[0]][next_use(rest, index) if parts[1] is None else kind(parts[1])] += 1
    return uses


def next_use(rest: list[str], index: int) -> str:
    if index + 1 == len(rest):
        return LAST
    return NEXT_OPTION if option_parts(rest[index + 1]) or rest[index + 1] == OPTIONS_END else kind(rest[index + 1])


def takes_value(uses: Counter) -> bool:
    total = sum(uses.values())
    kinds = Counter()
    for name, count in uses.items():
        kinds.update({KIND_FAMILIES.get(name, name): count} if name not in {LAST, NEXT_OPTION} else {})
    interrupted = uses[LAST] + uses[NEXT_OPTION]
    return total >= VALUE_OCCURRENCES and interrupted <= VALUE_INTERRUPTIONS * total and bool(kinds) and kinds.most_common(1)[0][1] >= VALUE_KIND_SHARE * total


# a command's words as options and arguments, each with its kind and its value: --oneline -n 5 a..b is (--oneline, flag, ""), (-n, number, 5), ("", range, a..b);
# -Sword is -S with its value when -S takes one attached, and the words after -- are arguments
def items(rest: list[str], valued: set[str], attached: set[str]) -> list[tuple[str, str, str]]:
    found, index, ended = [], 0, False
    while index < len(rest):
        if not ended and rest[index] == OPTIONS_END:
            ended, index = True, index + 1
            continue
        parts = None if ended else SHORT_ATTACHED.fullmatch(rest[index]).groups() if rest[index] in attached else option_parts(rest[index])
        takes = parts is not None and parts[1] is None and parts[0] in valued and index + 1 < len(rest)
        value = rest[index] if parts is None else parts[1] if parts[1] is not None else rest[index + 1] if takes else None
        found.append((parts[0] if parts else "", FLAG if value is None else kind(value), value or ""))
        index += 2 if takes else 1
    return found


# the short options a program's corpus shows taking a value attached, -Schevron, -Srouted: seen with ATTACHED_VALUES values whose
# letters are not all its flags, each word fewer than ATTACHED_WORD times, so -rn and -name stay what they are
def attached_options(uses: dict[str, Counter], valued: set[str]) -> set[str]:
    flags = {option[1] for option in uses if SHORT_OPTION.fullmatch(option) and option not in valued}
    words = [option for option, counted in uses.items() if SHORT_ATTACHED.fullmatch(option) and not set(option[2:]) <= flags and sum(counted.values()) < ATTACHED_WORD]
    return {option for option, count in Counter(word[:2] for word in words).items() if count >= ATTACHED_VALUES}


def form(name: str, found: list[tuple[str, str, str]]) -> str:
    collapsed: list[tuple[tuple[str, str], bool]] = []
    for option, value_kind, _ in found:
        item = (option, value_kind)
        collapsed = [*collapsed[:-1], (item, True)] if collapsed and collapsed[-1][0] == item else [*collapsed, (item, False)]
    return " ".join([name, *(shown(item, repeated) for item, repeated in collapsed)])


def shown(item: tuple[str, str], repeated: bool) -> str:
    option, value_kind = item
    more = "..." if repeated else ""
    if not option:
        return f"[<{value_kind}>{more}]"
    return f"[{option}{more}]" if value_kind == FLAG else f"[{option} <{value_kind}>{more}]"


# each run of a program by its subcommand path: the part it is, its line, and its options and arguments
def program_runs(runs: list[tuple[str, str, list[str]]]) -> dict[tuple[str, ...], list]:
    paths = subcommand_paths([rest for _, _, rest in runs])
    uses = option_uses([tail for _, tail in paths])
    valued = {option for option, counted in uses.items() if takes_value(counted)}
    starts = attached_options(uses, valued)
    attached = {option for option in uses if option[:2] in starts and SHORT_ATTACHED.fullmatch(option) and sum(uses[option].values()) < ATTACHED_WORD}
    subcommands: dict[tuple[str, ...], list] = defaultdict(list)
    for (part_id, line_id, _), (path, tail) in zip(runs, paths):
        subcommands[path].append((part_id, line_id, items(tail, valued | starts, attached)))
    return subcommands


def program_file(program: str, subcommands: dict[tuple[str, ...], list]) -> dict:
    return {
        "program": program,
        "lines": len({line_id for runs in subcommands.values() for _, line_id, _ in runs}),
        "parts": len({part_id for runs in subcommands.values() for part_id, _, _ in runs}),
        "subcommands": {" ".join(path) or NO_SUBCOMMAND: subcommand(program, path, subcommands[path]) for path in sorted(subcommands)},
        "values": kind_table(subcommands),
    }


def subcommand(program: str, path: tuple[str, ...], runs: list) -> dict:
    options = Counter(option for _, _, found in runs for option, _, _ in found if option)
    option_kinds = {option: Counter(value_kind for _, _, found in runs for named, value_kind, _ in found if named == option) for option in options}
    forms: dict[str, list[str]] = defaultdict(list)
    for part_id, _, found in runs:
        forms[form(" ".join([program, *path]), found)].append(part_id)
    return {
        "lines": len({line_id for _, line_id, _ in runs}),
        "parts": len({part_id for part_id, _, _ in runs}),
        "options": {option: {"seen": seen, "value": option_kinds[option].most_common(1)[0][0]} for option, seen in options.most_common()},
        "arguments": dict(Counter(value_kind for _, _, found in runs for option, value_kind, _ in found if not option).most_common()),
        "forms": [{"form": shape, "seen": len(ids), "sample_parts": sorted(set(ids))[:SAMPLE_IDS]} for shape, ids in sorted(forms.items(), key=lambda entry: (-len(entry[1]), entry[0]))],
    }


# the kinds of value a program is given that recur, each with how often it fills an argument and which options take it
def kind_table(subcommands: dict[tuple[str, ...], list]) -> dict:
    filled = [(option, value_kind) for runs in subcommands.values() for _, _, found in runs for option, value_kind, _ in found if value_kind != FLAG]
    seen = Counter(value_kind for _, value_kind in filled)
    as_argument = Counter(value_kind for option, value_kind in filled if not option)
    options: dict[str, Counter] = defaultdict(Counter)
    for option, value_kind in filled:
        options[value_kind].update([option] if option else [])
    return {value_kind: {"seen": count, "as_argument": as_argument[value_kind], "options": dict(options[value_kind].most_common())} for value_kind, count in seen.most_common() if count >= RECURRING}


# each slot a program's run fills with a value: an option by its name, an argument by its place, as argument 2
def filled_slots(found: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    slots, place = [], 0
    for option, value_kind, value in found:
        place += 0 if option else 1
        slots += [(option or f"argument {place}", value_kind, value)] if value_kind != FLAG else []
    return slots


@lru_cache(maxsize=None)
def scrubbed(value: str) -> str:
    return anonymised(value.replace(SUBSTITUTION, "$(...)"), [])


def rows(path: Path) -> list[dict]:
    return [json.loads(row) for row in path.read_text().splitlines() if row] if path.exists() else []


# every distinct value, scrubbed, by an ID kept from the last run, with its kind, how often it was given, the slots it filled most and a
# few of the parts it came from
def value_rows(runs_by_program: dict[str, dict[tuple[str, ...], list]], known: dict[str, str], taken: set[str]) -> list[dict]:
    counts: Counter = Counter()
    slots: dict[str, Counter] = defaultdict(Counter)
    samples: dict[str, set[str]] = defaultdict(set)
    kinds: dict[str, str] = {}
    for program, subcommands in runs_by_program.items():
        for path, runs in subcommands.items():
            for part_id, _, found in runs:
                for slot, value_kind, value in filled_slots(found):
                    shown_value = scrubbed(value)
                    counts[shown_value] += 1
                    slots[shown_value][" ".join([program, *path, slot])] += 1
                    samples[shown_value].update([part_id] if len(samples[shown_value]) < SAMPLE_IDS else [])
                    kinds.setdefault(shown_value, value_kind)
    taken.update(known.values())
    return [{"id": known.get(value) or new_id(taken), "value": value, "kind": kinds[value], "count": count, "slots": dict(slots[value].most_common(SAMPLE_IDS)), "sample_parts": sorted(samples[value])}
            for value, count in sorted(counts.items())]


# the IDs of a line's parts: the line's own for a line of one part, else those the last run gave it, else new ones
def part_ids(line_id: str, count: int, known: dict[str, list[str]], taken: set[str]) -> list[str]:
    if count == 1:
        return [line_id]
    kept = known.get(line_id, [])
    return kept if len(kept) == count else [new_id(taken) for _ in range(count)]


# a line's parts joined as written, each part by its ID followed by its redirects: [a, &&, (, b, 2>&1, |, c, )]
def chain(pieces: list[tuple], ids: list[str]) -> list[str]:
    found, next_id = [], iter(ids)
    for piece in pieces:
        found += [piece[1]] if piece[0] == "operator" else [next(next_id), *piece[3]]
    return found


# each program's file name, told apart from another's on a file system that ignores case: Journal beside journal is Journal-2
def file_names(programs: list[str]) -> dict[str, str]:
    names, taken = {}, Counter()
    for program in programs:
        name = re.sub(r"[^\w.+()-]", "-", program)
        taken[name.casefold()] += 1
        names[program] = f"{name}-{taken[name.casefold()]}.json" if taken[name.casefold()] > 1 else f"{name}.json"
    return names


# the corpus read in one pass: each program's runs, the chain of each line of more than one part, every part, the splitter's faults per
# line, and the line of each part whose line the splitter split well
def read_corpus(corpus: Path, known: dict[str, list[str]], taken: set[str], mapper) -> tuple[dict, list, list, dict, dict]:
    runs: dict[str, list] = defaultdict(list)
    chains, parts, faults, part_lines, fresh = [], [], {}, {}, []
    copied = corpus.with_name(corpus.name + ".writing")
    with copied.open("w") as copy:
        for line_id, line_pieces, line_faults in mapper(read_line, identified(corpus, copy, taken, fresh)):
            line_parts = [piece for piece in line_pieces if piece[0] == "part"]
            ids = part_ids(line_id, len(line_parts), known, taken)
            chains += [{"line": line_id, "chain": chain(line_pieces, ids)}] if len(line_parts) > 1 else []
            faults.update({line_id: line_faults} if line_faults else {})
            read = [] if line_faults else list(zip(ids, line_parts))
            parts += [(part_id, piece[1]) for part_id, piece in read]
            part_lines.update({part_id: line_id for part_id, _ in read})
            for part_id, piece in read:
                for program, rest in piece[2]:
                    runs[program].append((part_id, line_id, rest))
    if fresh:
        os.replace(copied, corpus)
    else:
        copied.unlink()
    return runs, chains, parts, faults, part_lines


# a form seen once among the many parts of its program, which is often a fragment of a part split wrongly
def lone_forms(files: dict[str, dict], part_lines: dict[str, str]) -> list[tuple[str, str]]:
    return [(part_lines[entry["sample_parts"][0]], f"lone form: the only one of {data['parts']} {program} parts read as {entry['form']}")
            for program, data in files.items() if data["parts"] >= LONE_FORM_PARTS
            for found in data["subcommands"].values() for entry in found["forms"] if entry["seen"] == 1]


# the parts of the lines split well, in chunks bash -n reads at once
def bash_chunks(bash: str, parts: list[tuple[str, str]]) -> Iterator[tuple[str, list[tuple[str, str]]]]:
    for start in range(0, len(parts), BASH_CHUNK):
        yield bash, parts[start:start + BASH_CHUNK]


# the parts of a chunk bash -n rejects on their own
def bash_rejected(entry: tuple[str, list[tuple[str, str]]]) -> list[str]:
    bash, chunk = entry
    texts = [text for _, text in chunk]
    return [chunk[index][0] for index in rejected_in(bash, texts, 0, len(texts))]


# the texts from start to end bash -n rejects on their own: they are read as one script, and where it stops the text it stops in is read
# alone, or, when that one parses, the first text from which on they no longer parse; the texts before it are read again, as an error
# bash reports first may stand after one it passed over
def rejected_in(bash: str, texts: list[str], start: int, end: int) -> list[int]:
    rejected = []
    while start < end and (line := parse_error(bash, texts[start:end])):
        stopped = min(part_at(texts, start, line), end - 1)
        culprit = stopped if parse_error(bash, texts[stopped:stopped + 1]) else first_failing(bash, texts, start, stopped)
        rejected += rejected_in(bash, texts, start, culprit) if culprit > start else []
        rejected += [culprit] if culprit == stopped or parse_error(bash, texts[culprit:culprit + 1]) else []
        start = culprit + 1
    return rejected


# the line bash -n stops at in the texts read as one script, 0 when they parse
def parse_error(bash: str, texts: list[str]) -> int:
    result = subprocess.run([bash, "-n"], input="\n".join(texts) + "\n", capture_output=True, text=True, timeout=BASH_TIMEOUT)
    stopped = re.search(r"line (\d+):", result.stderr)
    return 0 if result.returncode == 0 else int(stopped.group(1)) if stopped else sum(text.count("\n") + 1 for text in texts)


# the text from start on that holds the given line of them read as one script
def part_at(texts: list[str], start: int, line: int) -> int:
    lines = 0
    for index in range(start, len(texts)):
        lines += texts[index].count("\n") + 1
        if lines >= line:
            return index
    return len(texts) - 1


# the last text of the fewest from start on that bash -n fails to read, at most stopped
def first_failing(bash: str, texts: list[str], start: int, stopped: int) -> int:
    low, high = start + 1, stopped + 1
    while low < high:
        middle = (low + high) // 2
        low, high = (low, middle) if parse_error(bash, texts[start:middle]) else (middle + 1, high)
    return low - 1


def bash_faults(bash: str, parts: list[tuple[str, str]], part_lines: dict[str, str], mapper) -> list[tuple[str, str]]:
    if not bash:
        return []
    return [(part_lines[part_id], f"bash -n: part {part_id} does not parse on its own") for rejected in mapper(bash_rejected, bash_chunks(bash, parts)) for part_id in rejected]


# an output's data with every string in it but an ID scrubbed of a home folder, an email, a key or a token that slipped past the corpus's own
# scrubbing, before it is written
def scrubbed_data(data):
    if isinstance(data, str):
        return data if PART_ID.fullmatch(data) else scrubbed(data)
    if isinstance(data, dict):
        return {scrubbed_data(key): scrubbed_data(value) for key, value in data.items()}
    return [scrubbed_data(item) for item in data] if isinstance(data, list) else data


def write_jsonl(path: Path, found: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in found))


def write_forms(folder: Path, files: dict[str, dict]) -> None:
    folder.mkdir(exist_ok=True)
    for stale in folder.glob("*.json"):
        stale.unlink()
    names = file_names(sorted(files, key=lambda program: -files[program]["parts"]))
    for program, data in files.items():
        (folder / names[program]).write_text(ID_LIST.sub(lambda ids: "[" + re.sub(r",\s+", ", ", ids.group(1)) + "]", json.dumps(scrubbed_data(data), indent=1)) + "\n")


# reads the corpus beside which every output is written, with bash, when it is at hand, checking each part on its own
def written(corpus: Path, bash: str, line_mapper=map, chunk_mapper=map) -> dict[str, dict]:
    folder = corpus.parent
    known = {row["line"]: [token for token in row["chain"] if PART_ID.fullmatch(token)] for row in rows(folder / "chains.jsonl")}
    taken = {part_id for ids in known.values() for part_id in ids}
    runs, chains, parts, faults, part_lines = read_corpus(corpus, known, taken, line_mapper)
    subcommands = {program: program_runs(runs[program]) for program in sorted(runs)}
    files = {program: program_file(program, subcommands[program]) for program in subcommands}
    for line_id, fault in lone_forms(files, part_lines) + bash_faults(bash, parts, part_lines, chunk_mapper):
        faults[line_id] = [*faults.get(line_id, []), fault]
    write_forms(folder / "forms", files)
    known_values = {row["value"]: row["id"] for row in rows(folder / "values.jsonl")}
    write_jsonl(folder / "values.jsonl", scrubbed_data(value_rows(subcommands, known_values, taken)))
    write_jsonl(folder / "chains.jsonl", chains)
    (folder / "splitter-report.txt").write_text("".join(f"{line_id}\t{scrubbed('; '.join(reasons))}\n" for line_id, reasons in faults.items()))
    (folder / "parts.txt").unlink(missing_ok=True)
    return files


def main(corpus: Path) -> None:
    with multiprocessing.Pool() as pool:
        files = written(corpus, shutil.which("bash") or "", partial(pool.imap, chunksize=200), pool.imap)
    sizes = {path.name: path.stat().st_size for path in corpus.parent.iterdir() if path.is_file()}
    forms = sum(path.stat().st_size for path in (corpus.parent / "forms").glob("*.json"))
    print(f"{len(files)} program files of {forms} bytes beside {corpus.name} of {sizes[corpus.name]} bytes; {', '.join(f'{name} {size}' for name, size in sorted(sizes.items()) if name != corpus.name)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
