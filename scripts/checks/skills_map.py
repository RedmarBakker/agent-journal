"""Fails on a skill the journal map's table does not name and on a sentence two skills both say, the shared pin and button text aside. Run from the repository: PYTHONPATH=src python3 scripts/checks/skills_map.py."""

import re
import sys
from collections import defaultdict

from journal.features.pins.support.pin_and_button_text import PinAndButtonText
from journal.features.standard import Standard
from journal.support.skill import Skill

MAP = "journal"
# the text two skills hold on purpose, word for word
SHARED = (PinAndButtonText.BULLETS,)
# a sentence shorter than this is a phrase any two skills may share
SHORTEST_SENTENCE = 40


def shipped() -> list[Skill]:
    return [skill for feature in Standard.FEATURES for skill in (feature.skill, *feature.companion_skills) if skill]


def unnamed(skills: list[Skill]) -> list[str]:
    table = "\n".join(line for skill in skills if skill.name == MAP for line in skill.body.splitlines() if line.startswith("| "))
    return [skill.name for skill in skills if skill.name != MAP and not re.search(rf"(?<![\w-]){re.escape(skill.name)}(?![\w-])", table)]


def sentences(body: str) -> set[str]:
    for shared in SHARED:
        body = body.replace(shared, "")
    prose = " ".join(line.strip().removeprefix("- ") for line in body.splitlines() if line.strip() and not line.startswith(("#", "|")))
    return {sentence for sentence in re.split(r"(?<=[.!?])\s+", prose) if len(sentence) >= SHORTEST_SENTENCE}


def repeated(skills: list[Skill]) -> dict[str, list[str]]:
    holders = defaultdict(list)
    for skill in skills:
        for sentence in sentences(skill.body):
            holders[sentence].append(skill.name)
    return {sentence: names for sentence, names in holders.items() if len(names) > 1}


def problems(skills: list[Skill]) -> list[str]:
    missing = [f"the journal map's table names no row for the {name} skill, so no agent is pointed to it" for name in unnamed(skills)]
    twice = [f"{' and '.join(names)} both say: {sentence}" for sentence, names in repeated(skills).items()]
    return [*missing, *twice]


if __name__ == "__main__":
    text = problems(shipped())
    print("\n".join(text) if text else "every skill is named on the journal map and no sentence is in two skills")
    sys.exit(1 if text else 0)
