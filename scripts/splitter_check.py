"""Splits the lines of the command corpus with the journal's own Chain and lists the lines it may split wrongly, by the check that caught them, leaving out the lines already decided as split right; a full run writes the failing lines' IDs, and a run with --failing checks only those, so the list is drained before the next full run. Builds nothing else. Run from the repository: PYTHONPATH=src python3 -m scripts.splitter_check <corpus> --decided <file> --report <file> [--failing <file>] [--only-failing]."""

import argparse
import hashlib
import json
import re
import subprocess
import multiprocessing
import time
from collections import Counter, defaultdict
from pathlib import Path

from journal.support.chain import Chain
from scripts.corpus_commands import refused_inside_repository
from scripts.corpus_forms import ID_ALPHABET, splitter_faults, staged

WORKERS = 4
CHUNK_LINES = 500
SAMPLE_LINES = 20
PROGRESS_LINES = 5000
SHFMT_SECONDS = 10
BINARY = "BinaryCmd"
SPLIT_OPERATORS = {"&&"}
JOINED_OPERATORS = {"||", "|", "|&"}
PIPES_CHECK = "pipes"
UNPARSED = "unparsed: shfmt cannot read the line as bash, so only the gaps between its parts are judged"
OPENER_CHAIN = re.compile(r"<<-?\s*['\"]?\w+['\"]?.*(?:&&|\|\||;|\|)")
PART_CHECKS = ("open at end", "part start")
PART_NUMBER = re.compile(r"part (\d+)")
JOINED_CHECK = "joined"
ALLOWED_GAP = re.compile(r"(?:\s|;|&&|&|\\\n|#[^\n]*)*")
SHLEX_CHECK = "shlex"
UNCOUNTABLE = re.compile(r"[{}#]|\bcase\b|\(\)")


def corpus_lines(corpus: Path, only: set[str] | None):
    with corpus.open(errors="replace") as lines:
        for raw in lines:
            text = json.loads(raw) if raw.startswith('"') else ""
            line_id = content_id(text) if text else ""
            if text and (only is None or line_id in only):
                yield line_id, text


# a readable ID drawn from the line itself, the same on every run with no stored map: four groups of four letters
def content_id(text: str) -> str:
    digest = int.from_bytes(hashlib.blake2b(text.encode(), digest_size=10).digest())
    letters = "".join(ID_ALPHABET[(digest >> (5 * index)) & 31] for index in range(16))
    return "-".join(letters[index:index + 4] for index in range(0, 16, 4))


def line_faults(entry: tuple[str, str]) -> tuple[str, str, list[str]]:
    line_id, text = entry
    chained = Chain.chained(text)
    faults = [fault for fault in splitter_faults(text, chained, staged(chained)) if is_judged(fault, text)] + gap_faults(text)
    if not faults and not UNCOUNTABLE.search(text):
        return line_id, text, faults
    parsed = shfmt_parts(text)
    if parsed is None:
        return line_id, text, [fault for fault in faults if fault.split(":")[0] == JOINED_CHECK] or [UNPARSED]
    counted = [f"shfmt: shfmt reads {parsed} parts where Chain reads {len(chained)}"] if parsed != len(chained) and not is_chained_opener(chained) else []
    return line_id, text, counted + [fault for fault in faults if fault.split(":")[0] != SHLEX_CHECK and not is_parsed_part(fault, chained)]


# decided: commands chained on a heredoc's opener line (git commit -F - <<'MSG' && git log) stay one part with the body, since the body
# belongs to the first of them and splitting them would cut the line's text out of order; shfmt counts them apart
def is_chained_opener(chained: list[tuple[str, str]]) -> bool:
    return any(OPENER_CHAIN.search(part.split("\n")[0]) for _, part in chained)


# a part shfmt parses on its own is no part cut in the middle, whatever the quote and bracket count says
def is_parsed_part(fault: str, chained: list[tuple[str, str]]) -> bool:
    numbered = PART_NUMBER.search(fault)
    return fault.split(":")[0] in PART_CHECKS and bool(numbered) and shfmt_parts(chained[int(numbered.group(1)) - 1][1]) is not None


# the parts the journal's splitter should give, by a real shell parser: one per statement, a && chain splitting into its commands and
# a pipeline or a || chain staying one part; none when shfmt cannot parse the line
def shfmt_parts(text: str) -> int | None:
    parsed = subprocess.run(["shfmt", "--tojson"], input=text.encode(), capture_output=True, timeout=SHFMT_SECONDS)
    if parsed.returncode:
        return None
    return sum(command_parts(statement["Cmd"]) for statement in json.loads(parsed.stdout)["Stmts"] if statement.get("Cmd"))


def command_parts(command: dict) -> int:
    if command.get("Type") != BINARY or command.get("Op") not in SPLIT_OPERATORS | JOINED_OPERATORS:
        return 1
    joined = command_parts(command["X"]["Cmd"]) + command_parts(command["Y"]["Cmd"])
    return joined if command["Op"] in SPLIT_OPERATORS else joined - 1


# the pipes check judges the corpus script's own pipe splitter, not Chain, which keeps a pipeline in one part; the shlex count cannot read
# a group, a function, a case or a comment, which Chain keeps whole, so it judges only lines with none of them
def is_judged(fault: str, text: str) -> bool:
    check = fault.split(":")[0]
    return check not in (PIPES_CHECK, JOINED_CHECK) and (check != SHLEX_CHECK or not UNCOUNTABLE.search(text))


# what lies between two parts the splitter gives may only be space, a separator, a line continuation or a comment; anything else was lost
def gap_faults(text: str) -> list[str]:
    spans = Chain.spans(text)
    ends = [0, *(end for _, _, _, end in spans)]
    gaps = [text[ends[index]:start] for index, (_, _, start, _) in enumerate(spans)] + [text[ends[-1]:]]
    lost = [gap.strip() for gap in gaps if not ALLOWED_GAP.fullmatch(gap)]
    return [f"joined: the splitter dropped {json.dumps(lost[0][:40])} between its parts"] if lost else []


def decided_lines(path: Path | None) -> set[str]:
    return {row.split("\t")[0] for row in path.read_text().splitlines() if row.strip()} if path and path.is_file() else set()


def report(faults: dict[str, list[tuple[str, str]]], checked: int, seconds: float) -> str:
    counts = Counter({check: len(found) for check, found in faults.items()})
    head = [f"{checked} lines checked in {seconds:.0f} s; {sum(counts.values())} suspect by check:", *(f"  {check}: {count}" for check, count in counts.most_common()), ""]
    body = [f"== {check} ({len(found)}) ==\n" + "\n".join(f"{line_id}\t{reason}\t{json.dumps(line[:300])}" for line_id, reason, line in found[:SAMPLE_LINES]) for check, found in sorted(faults.items(), key=lambda item: -len(item[1]))]
    return "\n".join(head + body) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--decided", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--failing", type=Path, default=None, help="the file of failing line IDs: written by a full run, read with --only-failing")
    parser.add_argument("--only-failing", action="store_true", help="check only the lines the last full run found failing")
    args = parser.parse_args()
    for written in (args.report, args.failing, args.decided):
        if written:
            refused_inside_repository(written)
    only = decided_lines(args.failing) if args.only_failing else None
    decided, began, checked, unread = decided_lines(args.decided), time.monotonic(), 0, 0
    faults: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    with multiprocessing.Pool(WORKERS) as pool:
        total = sum(1 for _ in corpus_lines(args.corpus, only))
        for line_id, line, found in pool.imap(line_faults, corpus_lines(args.corpus, only), chunksize=CHUNK_LINES):
            checked += 1
            if checked % PROGRESS_LINES == 0 or checked == total:
                print(f"checked {checked}/{total}", flush=True)
            if line_id in decided:
                continue
            if found == [UNPARSED]:
                unread += 1
                continue
            for reason in found:
                faults[reason.split(":")[0]].append((line_id, reason, line))
    text = report(faults, checked, time.monotonic() - began) + f"{unread} lines shfmt cannot read as bash, judged only by their gaps\n"
    if args.failing:
        failing_ids = sorted({line_id for found in faults.values() for line_id, _, _ in found})
        args.failing.write_text("".join(f"{line_id}\n" for line_id in failing_ids))
    if args.report:
        args.report.write_text(text)
    print(text.split("\n\n")[0])


if __name__ == "__main__":
    main()
