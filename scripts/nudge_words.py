"""Writes the fixed words of every registered nudge into .commandments/custom/lists.json as nudge_words: each run of at least WORDS words between a nudge's blanks, in its title or its brief, so the rule NudgeWordsInTestDetector finds a test that checks a nudge by its words. Run from the repository: PYTHONPATH=src python3 -m scripts.nudge_words."""

import json
import re
from pathlib import Path

from journal.engine.engine_nudges import EngineNudges
from journal.engine.nudge import Nudge
from journal.features.standard import Standard

LISTS = Path(__file__).resolve().parents[1] / ".commandments" / "custom" / "lists.json"
# a run of fewer words is common enough to stand in a test's own text
WORDS = 4
BLANK = re.compile(r"\{\{\w+(?:\|cap=\d+)?\}\}")
# runs the journal's other text writes too, as a plugin's or a service's log does, which a test of that text holds without checking a nudge
COMMON = ("times in a row",)
EDGES = " .,:;"


def registered() -> list[Nudge]:
    return [*EngineNudges.ALL, *(nudge for feature in Standard.FEATURES for nudge in feature.nudges)]


def words(nudges: list[Nudge]) -> list[str]:
    runs = {run.strip(EDGES) for nudge in nudges for text in (nudge.title, nudge.brief) for run in BLANK.split(text)}
    return sorted(run for run in runs if len(run.split()) >= WORDS and run not in COMMON)


def written() -> None:
    lists = json.loads(LISTS.read_text())
    LISTS.write_text(json.dumps({**lists, "nudge_words": words(registered())}, indent=4) + "\n")


if __name__ == "__main__":
    written()
