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


def applied(row: dict, options: list[str]) -> dict:
    found = {"kind": row.get("kind", "unknown"), "effects": set(row.get("effects", [])), "uncertain": row.get("uncertain", False)}
    for option in options:
        modifier = resolved(row.get("modifiers", {}), option)
        found["kind"] = modifier.get("kind", found["kind"])
        found["effects"] |= set(modifier.get("effects", []))
        found["uncertain"] = found["uncertain"] or modifier.get("uncertain", False)
    return found


def classified(table: dict, program: str, subcommand: str, form: str) -> dict:
    if program in table["wrappers"]:
        return {"kind": "wrapper", "effects": set(), "uncertain": False}
    row = resolved(table["programs"], program)
    if not row:
        return {**table["unknown"], "effects": set(), "uncertain": False}
    base = row.get("base", row)
    sub = resolved(row.get("subcommands", {}), subcommand.split()[0]) if subcommand and not subcommand.startswith("(") else {}
    options = OPTION.findall(form)
    return applied({**base, **sub, "modifiers": {**row.get("modifiers", {}), **sub.get("modifiers", {})}}, options)


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
