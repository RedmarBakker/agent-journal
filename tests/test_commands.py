"""Every journal command, noun and verb, run in order on one seeded journal from tests/commands/invocations.txt, its output compared with the frozen tests/commands/expected.txt; re-frozen on purpose with COMMANDS_FREEZE=1, as the replays are."""
import os
import re
import shlex
from pathlib import Path

import pytest
from journal.support.caller import Caller
from test_features import AGENT, USER, booted

FOLDER = Path(__file__).parent / "commands"
INVOCATIONS = FOLDER / "invocations.txt"
EXPECTED = FOLDER / "expected.txt"
CALLERS = {"agent": AGENT, "user": USER}
# what differs from one run to the next, put in a word of its own so the frozen output holds
VARYING = (
    (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?([+-]\d{2}:\d{2}|Z)?"), "<time>"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), "<date>"),
    (re.compile(r"\b\d{1,2}:\d{2}(:\d{2})?\b"), "<clock>"),
    (re.compile(r"\bat \d{1,2}\.\d{2}\b"), "at <clock>"),
    (re.compile(r"\b\d+(\.\d+)? ?(ms|s|seconds?|minutes?|hours?|days?)\b"), "<span>"),
    (re.compile(r"\b1[78]\d{8}(\.\d+)?\b"), "<epoch>"),
    (re.compile(r"127\.0\.0\.1:\d+|localhost:\d+"), "<address>"),
    (re.compile(r"\b[0-9a-f]{12,}\b"), "<hex>"),
    (re.compile(r"\bload [\d. ]+ on \d+ cores, [\d,]+ MB free(; [\d.]+ beyond what \d+ test runs going explain)?"), "load <machine>"),
)
DOCUMENT = "## The cart\n\nThe cart adds its lines and the tax once.\n\n## Rounding\n\nMoney is rounded to cents.\n"


@pytest.fixture(scope="module")
def boot():
    return booted


def invocations() -> list[tuple[str, list[str]]]:
    rows = [line for line in INVOCATIONS.read_text().splitlines() if line.strip() and not line.startswith("#")]
    return [(row.split(" ", 1)[0], shlex.split(row.split(" ", 1)[1])) for row in rows]


def normalised(text: str, root: Path) -> str:
    text = text.replace(str(root.resolve()), "<root>").replace(str(root), "<root>")
    for pattern, word in VARYING:
        text = pattern.sub(word, text)
    return text.rstrip()


def section(caller: str, argv: list[str], outcome, root: Path) -> str:
    printed = normalised("\n".join(part for part in (outcome.text, outcome.error) if part), root)
    return f"$ {caller}: journal {normalised(shlex.join(argv), root)}\nexit {outcome.code}\n{printed}"


def test_every_command_of_the_console_has_an_invocation(app):
    console = app.console()
    named = {tuple(console.with_verb(argv)[:2]) for _, argv in invocations()}
    verbs = {(noun, verb) for noun, command in console.commands.items() for verb in console.verbs(command)}
    missing = sorted(verbs - named)
    assert not missing, f"commands with no line in {INVOCATIONS.name}: {', '.join(' '.join(pair) for pair in missing)}"


def test_every_command_prints_what_it_printed_when_frozen(app):
    document = app.config.root / "cart.md"
    document.write_text(DOCUMENT)
    console = app.console()
    sections = []
    for caller, argv in invocations():
        argv = [str(document) if word == "{file}" else word for word in argv]
        sections.append(section(caller, argv, console.run(argv, CALLERS[caller]), app.config.root))
    printed = "\n\n".join(sections) + "\n"
    if os.environ.get("COMMANDS_FREEZE") == "1":
        EXPECTED.write_text(printed)
    frozen = EXPECTED.read_text().split("\n\n$ ")
    changed = [f"$ {now}" if index else now for index, (now, then) in enumerate(zip(printed.split("\n\n$ "), frozen)) if now != then]
    assert len(frozen) == len(sections) and not changed, "commands whose output changed (re-freeze with COMMANDS_FREEZE=1 when the change is meant):\n\n" + "\n\n".join(changed[:5])
