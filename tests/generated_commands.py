"""A test helper, not a test: builds a seeded sample of shell commands from the forms and chain shapes in tests/generated/forms.json, each with the classification its forms give it read from the command table, so every reader of commands can be checked against it."""
import json
import random
from dataclasses import dataclass
from pathlib import Path

from journal.support.classification import Classification
from scripts.classification_coverage import TABLE, classified
from scripts.splitter_fixture import filled

FIXTURE = Path(__file__).parent / "generated" / "forms.json"
# the operators that end a part of a chain, as Chain splits it; a pipe and an || keep their commands in one part
PART_ENDS = ("&&", ";")


@dataclass(frozen=True)
class GeneratedCommand:
    """A generated shell line: its text, the forms it was filled from with the text each became, how many parts Chain cuts it into, and the classification its forms give it."""

    text: str
    forms: tuple[tuple[dict, str], ...]
    parts: int
    expected: Classification


class Generator:
    """Picks a chain shape and a form for each of its commands from the fixture, fills each form's slots with generated values, and joins them as the shape says, all from one seed, so a run draws the same sample every time."""

    def __init__(self, seed: int) -> None:
        fixture = json.loads(FIXTURE.read_text())
        self.table = json.loads(TABLE.read_text())
        self.forms = [form for form in fixture["forms"] if self.expected(form).kind != "wrapper"]
        self.chains = fixture["chains"]
        self.rng = random.Random(seed)

    def commands(self, count: int) -> list[GeneratedCommand]:
        return [self.command(self.rng.choice(self.chains) if self.rng.random() < 0.5 else ["PART"]) for _ in range(count)]

    def command(self, shape: list[str]) -> GeneratedCommand:
        forms = [(form, filled(form["form"], self.rng)) for form in (self.rng.choice(self.forms) for token in shape if token == "PART")]
        texts, words = iter(text for _, text in forms), []
        for token in shape:
            words.append(next(texts) if token == "PART" else token)
        expected = Classification.union(self.expected(form) for form, _ in forms)
        return GeneratedCommand(" ".join(words), tuple(forms), 1 + sum(token in PART_ENDS for token in shape), expected)

    def expected(self, form: dict) -> Classification:
        found = classified(self.table, form["program"], form["subcommand"], form["form"])
        return Classification(kind=found["kind"], effects=tuple(sorted(found["effects"])), uncertain=bool(found["uncertain"]))
