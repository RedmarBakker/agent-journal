"""Gives every form of the corpus its classification from src/journal/support/command_table.json, its program's base, the subcommand's and the options' modifiers applied, and prints how many forms are classified, uncertain, a wrapper or of an unknown program, with a sample to read by eye. Run from the repository: python3 -m scripts.classification_coverage <corpus folder>."""

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

from scripts.corpus_commands import refused_inside_repository

TABLE = Path(__file__).resolve().parents[1] / "src" / "journal" / "support" / "command_table.json"
SAMPLE_FORMS = 40
OPTION = re.compile(r"(?<![\w<])(--?[A-Za-z][\w-]*)")


def resolved(rows: dict, name: str) -> dict:
    found = rows.get(name, {})
    return resolved(rows, found["same_as"]) if "same_as" in found else found


# a row that names a kind replaces the effects before it, one that names none adds to them, as the classifier reads the table
def applied(row: dict, options: list[str]) -> dict:
    found = {"kind": row.get("kind", "unknown"), "effects": set(row.get("effects", [])), "uncertain": row.get("uncertain", False)}
    for option in options:
        modifier = resolved(row.get("modifiers", {}), option)
        found["effects"] = set(modifier.get("effects", [])) if "kind" in modifier else found["effects"] | set(modifier.get("effects", []))
        found["kind"] = modifier.get("kind", found["kind"])
        found["uncertain"] = found["uncertain"] or modifier.get("uncertain", False)
    return found


def is_wrapping(table: dict, program: str, form: str) -> bool:
    wrapper = resolved(table["wrappers"], program)
    words = form.split()[1:]
    return bool(wrapper) and (not wrapper.get("subcommands") or any(words[:len(subcommand.split())] == subcommand.split() for subcommand in wrapper["subcommands"]))


def classified(table: dict, program: str, subcommand: str, form: str) -> dict:
    if is_wrapping(table, program, form):
        return {"kind": "wrapper", "effects": set(), "uncertain": False}
    row = resolved(table["programs"], program)
    if not row:
        return {**table["unknown"], "effects": set(), "uncertain": False}
    levels = walked(row, form.split()[1:])
    named = next(level for level in reversed(levels) if "kind" in level or level is levels[0])
    after = levels[levels.index(named) + 1:]
    found = {**named, "effects": [effect for level in [named, *after] for effect in level.get("effects", [])], "uncertain": any(level.get("uncertain") for level in [named, *after]),
             "modifiers": {name: modifier for level in [row, *levels[1:]] for name, modifier in level.get("modifiers", {}).items()}}
    return applied(found, OPTION.findall(form))


# the activity a form is shown as: the label of the deepest row its words name that has one, or running its program
def labelled(table: dict, program: str, form: str) -> str:
    row = resolved(table["programs"], program)
    levels = walked(row, form.split()[1:]) if row else []
    modifiers = {name: modifier for level in [row or {}, *levels[1:]] for name, modifier in level.get("modifiers", {}).items()}
    named = [resolved(modifiers, option).get("label") for option in OPTION.findall(form)]
    return next((label for label in reversed(named) if label), next((level["label"] for level in reversed(levels) if "label" in level), f"running {program}"))


# the shape a form is known by: its program and the subcommands the table names below it
def shaped(table: dict, program: str, form: str) -> str:
    row = resolved(table["programs"], program)
    words = [word for word in form.split()[1:] if not word.startswith(("-", "<", "[", "("))]
    return " ".join([program, *words[:len(walked(row, form.split()[1:])) - 1]]) if row else program


# the rows a form's words name, its program's base and each subcommand below it, the options and slots between them passed over
def walked(row: dict, words: list[str]) -> list[dict]:
    levels, current = [row.get("base", row)], row
    for word in words:
        if word.startswith(("-", "<", "[", "(")):
            continue
        below = resolved(current.get("subcommands", {}), word)
        if not below:
            break
        levels, current = [*levels, below], below
    return levels


def main(corpus: Path) -> None:
    refused_inside_repository(corpus)
    table = json.loads(TABLE.read_text())
    counts, rows = Counter(), []
    for path in sorted((corpus / "forms").glob("*.json")):
        data = json.loads(path.read_text())
        for subcommand, found in data["subcommands"].items():
            for entry in found["forms"]:
                result = classified(table, data["program"], subcommand, entry["form"])
                counts["uncertain" if result["uncertain"] else result["kind"] if result["kind"] in ("wrapper", "unknown") else "classified"] += entry["seen"]
                rows.append((entry["seen"], entry["form"], result))
    print(f"{sum(counts.values())} form uses: " + ", ".join(f"{name} {count}" for name, count in counts.most_common()))
    known = [row for row in rows if row[2]["kind"] != "unknown"]
    for seen, form, result in random.Random(1).sample(known, min(SAMPLE_FORMS, len(known))):
        print(f"{seen:>6}  {form[:70]:<70}  {result['kind']}{' (uncertain)' if result['uncertain'] else ''}: {', '.join(sorted(result['effects'])) or 'no effect'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    main(parser.parse_args().corpus)
