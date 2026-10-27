"""Writes the splitter fixture, tests/splitter/lines.jsonl: shell lines rebuilt from the corpus forms of well-known programs, from the corpus's most common chain shapes and from made-up lines of every compound Chain reads (loops, cases, heredocs, groups, comments, continuations, the eval form Claude Code hands the runner, the journal's aliases), every value generated and none taken from the corpus, each line with the parts Chain splits it into, their kind and their pipe stages. Run from the repository: PYTHONPATH=src python3 -m scripts.splitter_fixture <corpus folder>."""

import argparse
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path

from journal.support.chain import Chain
from scripts.corpus_commands import refused_inside_repository
from scripts.corpus_forms import PART_ID

FIXTURE = Path(__file__).resolve().parents[1] / "tests" / "splitter" / "lines.jsonl"
PROGRAMS = {
    "awk", "cat", "cd", "chmod", "composer", "cp", "curl", "cut", "date", "diff", "docker", "du", "echo", "export",
    "find", "gh", "git", "go", "grep", "head", "jq", "journal", "kill", "ln", "ls", "lsof", "make", "mkdir", "mv",
    "node", "npm", "npx", "perl", "php", "pgrep", "printf", "ps", "pytest", "python", "python3", "rm", "sed", "sleep",
    "sort", "sqlite3", "ssh", "tail", "tee", "touch", "tr", "uniq", "vitest", "wc", "which", "xargs",
}
PLAIN_SUBCOMMAND = re.compile(r"[a-z][a-z-]{1,19}")
SUBCOMMANDS_KEPT = 10
FORMS_KEPT = 4
CHAIN_SHAPES_KEPT = 400
OPTIONAL_KEPT = 0.6
HEREDOC_BODY = "\nbody\nEOF"
REDIRECT_TARGETS = {">": "> out.log", ">>": ">> out.log", "<": "< notes.txt", "2>": "2> /dev/null"}
VALUES = {
    "word": ["alpha", "beta", "main", "status"], "path": ["src/app/main.py", "docs/notes.md", "build/out", "tests/test_app.py"],
    "pattern": ["'TODO'", "\"def run\"", "'^import'", "error"], "number": ["3", "20", "100"], "text": ["'a short note'", "\"two words\""],
    "glob": ["'*.py'", "src/*.js"], "string": ["'hello'", "\"value\""], "variable": ["$NAME", "\"$HOME\"", "${COUNT}"],
    "code": ["'print(1)'", "\"import sys; print(sys.path)\""], "file": ["notes.txt", "out.log"], "assignment": ["NAME=value", "COUNT=2"],
    "substitution": ["$(pwd)", "\"$(date +%s)\""], "branch": ["feature-x", "main"], "revision": ["HEAD~1", "abc1234"], "empty": ["''"],
    "url": ["https://example.com/api", "http://localhost:3000/"], "version": ["1.2.3"], "test name": ["test_app.py::test_runs"],
    "range": ["1,20p", "HEAD~3..HEAD"], "address": ["127.0.0.1"], "date": ["2.weeks.ago"], "number range": ["1-5"],
    "json": ["'{\"a\": 1}'"], "duration": ["30s"], "stdin": ["-"], "email": ["someone@example.com"],
}
SIMPLE = ["ls -la", "git status", "echo done", "pwd", "grep -n 'x' src/app.py", "npm test", "python3 -m pytest -q", "cat notes.txt"]
COMPOUNDS = [
    "for f in src/*.py; do {a}; done",
    "for f in a b c; do\n  {a}\n  {b}\ndone",
    "while read -r line; do {a}; done < notes.txt && {b}",
    "until {a}; do sleep 1; done; {b}",
    "if {a}; then {b}; else {c}; fi",
    "if {a}; then\n  {b}\nelif {c}; then\n  echo two\nfi",
    "case \"$1\" in\n  start) {a} ;;\n  stop) {b} | tail -1;;\n  *) echo none ;;\nesac",
    "{{ {a}; {b}; }} > out.log 2>&1",
    "( cd src && {a} ) && {b}",
    "result=$({a} | wc -l) && echo \"$result\"",
    "{a} <<'EOF'\nfirst line\nuntil done\nEOF\n{b}",
    "cat > notes.txt <<EOF && {a}\nbody for done\nEOF",
    "for f in a b; do\n  cat <<EOF\n$f\nEOF\ndone\n{a}",
    "out=$(cat <<'EOF'\nline\nEOF\n) && {a}",
    "( cat <<EOF\nbody\nEOF\n) | {a}",
    "{a} <<\\EOF\nbody\nEOF",
    "echo $((1<<3)) && {a}",
    "(( n = 1 << 2 )); {a}",
    "{a}\n# a comment on a line of its own\n{b}",
    "# only a comment",
    "{a} # a comment after a command",
    "\\\nfor f in a b; do {a}; done",
    "{a} \\\n  --flag value && {b}",
    "find . -name '*.pyc' -exec rm {{}} \\;; {a}",
    "grep -q done notes.txt && {a}",
    "{a} &\n{b}",
    "{a} & {b} & wait",
    "{a} || {b} && {c}",
    "{a} |& tee out.log",
    "{a} 2>&1 | tail -20",
    "eval '{a} && {b}' < /dev/null",
    "eval 'echo '\"'\"'quoted'\"'\"' && {a}' < /dev/null && pwd -P >| /tmp/cwd",
    "eval {a_word} < /dev/null && pwd -P >| /tmp/cwd",
    "journal splitter",
    "journal suite tests/test_app.py",
    "journal output read 12 --tail 20",
    "repeat 3 {a}",
    "foreach f (a b) {a}; end",
    "select x in a b; do {a}; break; done",
    "time {a}",
    "! {a} && {b}",
]


def generated(kind: str, rng: random.Random) -> str:
    return rng.choice(VALUES.get(kind, ["value"]))


def filled(form: str, rng: random.Random) -> str:
    optional = re.sub(r"\[([^\]]*)\]", lambda match: match.group(1) if rng.random() < OPTIONAL_KEPT else "", form)
    return " ".join(re.sub(r"<([^>]+)>", lambda match: generated(match.group(1), rng), optional).split())


def seeded(text: str) -> random.Random:
    return random.Random(hashlib.blake2b(text.encode(), digest_size=8).hexdigest())


def form_lines(forms: Path) -> list[str]:
    lines = []
    for program in sorted(PROGRAMS):
        path = forms / f"{program}.json"
        if not path.exists():
            continue
        subcommands = json.loads(path.read_text())["subcommands"]
        kept = sorted((name for name in subcommands if PLAIN_SUBCOMMAND.fullmatch(name) or name.startswith("(")), key=lambda name: -subcommands[name]["parts"])
        for name in kept[:SUBCOMMANDS_KEPT]:
            lines += [filled(form["form"], seeded(form["form"])) for form in subcommands[name]["forms"][:FORMS_KEPT]]
    return lines


def rendered(shape: tuple[str, ...], rng: random.Random) -> str:
    words, body = [rng.choice(SIMPLE)], ""
    for token in shape[1:]:
        if token == "<< heredoc":
            words, body = words + ["<<'EOF'"], HEREDOC_BODY
            continue
        if token == ";" and (body or rng.random() < 0.5):
            words, body = words + [body + "\n"], ""
            continue
        words += [rng.choice(SIMPLE) if token == "PART" else REDIRECT_TARGETS.get(token, token)]
    return " ".join(words).replace(" \n", "\n").replace("\n ", "\n") + body


def chain_lines(chains: Path) -> list[str]:
    shapes = Counter(tuple("PART" if PART_ID.fullmatch(token) else token for token in json.loads(row)["chain"]) for row in chains.read_text().splitlines())
    return [rendered(shape, seeded(" ".join(shape))) for shape, _ in shapes.most_common(CHAIN_SHAPES_KEPT)]


def compound_lines() -> list[str]:
    rng = seeded("compounds")
    return [template.format(a=rng.choice(SIMPLE), b=rng.choice(SIMPLE), c=rng.choice(SIMPLE), a_word=rng.choice(["ls", "pwd"])) for template in COMPOUNDS for _ in range(2)]


def row(line: str) -> dict:
    return {"line": line, "parts": [[part.text, part.kind(), part.stages()] for part in Chain.parts(line)]}


def main(corpus: Path) -> None:
    refused_inside_repository(corpus)
    lines = list(dict.fromkeys(form_lines(corpus / "forms") + chain_lines(corpus / "chains.jsonl") + compound_lines()))
    FIXTURE.parent.mkdir(exist_ok=True)
    FIXTURE.write_text("".join(json.dumps(row(line), ensure_ascii=False) + "\n" for line in lines))
    print(f"{len(lines)} lines written to {FIXTURE}, {FIXTURE.stat().st_size} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    main(parser.parse_args().corpus)
