"""Writes the generated-commands fixture, tests/generated/forms.json: the forms of the well-known programs several projects ran, each with its program and subcommand, and the corpus's most common chain shapes made of commands joined by &&, ;, | and || alone, from which tests/generated_commands.py builds a seeded sample of commands. Run from the repository: PYTHONPATH=src python3 -m scripts.generated_forms <corpus folder>."""

import argparse
import json
from pathlib import Path

from scripts.corpus_commands import PROJECT_COUNTS, refused_inside_repository
from scripts.splitter_fixture import chain_shapes, kept_forms

FIXTURE = Path(__file__).resolve().parents[1] / "tests" / "generated" / "forms.json"
# the tokens a generated chain is joined by: a command, the operators that join two, and the folding of errors into a pipe
CHAIN_TOKENS = {"PART", "&&", ";", "|", "||", "2>&1"}


def main(corpus: Path) -> None:
    refused_inside_repository(corpus)
    forms = [{"program": program, "subcommand": subcommand, "form": form} for program, subcommand, form in kept_forms(corpus / "forms", json.loads((corpus / PROJECT_COUNTS).read_text()))]
    shapes = [list(shape) for shape in chain_shapes(corpus / "chains.jsonl") if set(shape) <= CHAIN_TOKENS]
    FIXTURE.parent.mkdir(exist_ok=True)
    FIXTURE.write_text(json.dumps({"forms": forms, "chains": shapes}, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(forms)} forms and {len(shapes)} chain shapes written to {FIXTURE}, {FIXTURE.stat().st_size} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    main(parser.parse_args().corpus)
