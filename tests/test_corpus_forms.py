"""scripts/corpus_forms.py on a corpus of made-up groups: every line gets an ID kept beside it across runs, each line is split into parts with IDs of their own, the forms name kinds, counts and a few parts and never a literal value, the values file holds each distinct value scrubbed, the chains file joins the parts, and the splitter report names a line split wrongly by the check that found it."""

import json
from pathlib import Path

from scripts.corpus_forms import LINE_ID, PART_ID, written

GROUPS = [
    [
        "git log --oneline -n 5 main..HEAD",
        "cd repo && git log --oneline -n 12 a1b2c3d..HEAD | head -5",
        "git log --oneline -n 3 v1.0..v1.1 2>&1",
        "git log -Schevron --stat",
        "git log -Srouted --stat",
        "git log -S widget --stat",
        "git status --short",
        "git status --short | head -3",
        "git -C repo status --short",
        "git checkout -- src/a.py",
        "git checkout -- src/b.py",
        "git checkout main",
        "git shortlog --author jane@private.org",
    ],
    [
        "pytest -q tests/test_alpha.py",
        "uv run pytest -q tests/test_beta.py",
        "pytest tests/test_gamma.py -q",
    ],
    [
        "cat /Users/someone/notes.txt",
        'echo "unclosed && ls',
        "cat <<'EOF' && ls\\nbody\\nEOF",
    ],
]


def corpus(folder: Path) -> Path:
    path = folder / "all_commands.txt"
    path.write_text("\n\n".join("\n".join(group) for group in GROUPS) + "\n")
    return path


def line_ids(path: Path) -> dict[str, str]:
    return {raw[LINE_ID.match(raw).end():]: LINE_ID.match(raw).group(1) for raw in path.read_text().splitlines() if raw}


def outputs(folder: Path) -> dict[str, str]:
    return {path.relative_to(folder).as_posix(): path.read_text() for path in sorted(folder.rglob("*")) if path.is_file()}


def chains(folder: Path) -> dict[str, list[str]]:
    return {row["line"]: row["chain"] for row in map(json.loads, (folder / "chains.jsonl").read_text().splitlines())}


def test_each_line_gets_an_id_beside_it_kept_with_every_part_and_value_id_across_runs(tmp_path):
    path = corpus(tmp_path)
    written(path, "")
    first = outputs(tmp_path)
    written(path, "")
    assert outputs(tmp_path) == first
    raw = path.read_text()
    assert raw.count("\n\n") == len(GROUPS) - 1
    assert all(LINE_ID.match(row) for row in raw.splitlines() if row)
    assert sorted(line_ids(path)) == sorted(line for group in GROUPS for line in group)


def test_a_line_is_split_into_parts_joined_in_the_chains_file_and_a_line_of_one_part_is_its_own_part(tmp_path):
    path = corpus(tmp_path)
    written(path, "")
    ids = line_ids(path)
    cd, joined, log, piped, head = chains(tmp_path)[ids["cd repo && git log --oneline -n 12 a1b2c3d..HEAD | head -5"]]
    assert (joined, piped) == ("&&", "|") and all(PART_ID.fullmatch(part) for part in (cd, log, head))
    assert ids["git log --oneline -n 3 v1.0..v1.1 2>&1"] not in chains(tmp_path)


def test_the_forms_name_kinds_options_counts_and_a_few_parts_and_hold_no_literal_value(tmp_path):
    path = corpus(tmp_path)
    written(path, "")
    ids = line_ids(path)
    git = json.loads((tmp_path / "forms" / "git.json").read_text())
    log = git["subcommands"]["log"]
    piped_log = chains(tmp_path)[ids["cd repo && git log --oneline -n 12 a1b2c3d..HEAD | head -5"]][2]
    assert log["forms"][0] == {"form": "git log [--oneline] [-n <number>] [<range>]", "seen": 3, "sample_parts": sorted([
        ids["git log --oneline -n 5 main..HEAD"], piped_log, ids["git log --oneline -n 3 v1.0..v1.1 2>&1"]])}
    assert {"form": "git log [-S <word>] [--stat]", "seen": 3, "sample_parts": sorted(ids[line] for line in GROUPS[0][3:6])} in log["forms"]
    assert log["options"]["-n"] == {"seen": 3, "value": "number"} and log["options"]["-S"] == {"seen": 3, "value": "word"}
    assert not [option for option in log["options"] if option.startswith("-S") and option != "-S"]
    assert log["arguments"] == {"range": 3}
    assert git["subcommands"]["status"]["lines"] == 3 and git["lines"] == len(GROUPS[0])
    checkout = git["subcommands"]["checkout"]
    assert "--" not in checkout["options"] and checkout["forms"][0]["form"] == "git checkout [<path>]"
    pytest = json.loads((tmp_path / "forms" / "pytest.json").read_text())
    assert pytest["subcommands"]["(no subcommand)"]["forms"][0] == {"form": "pytest [-q] [<path>]", "seen": 2, "sample_parts": sorted(ids[line] for line in GROUPS[1][:2])}
    forms = "".join(text for name, text in outputs(tmp_path).items() if name.startswith("forms/"))
    assert not any(literal in forms for literal in ("main..HEAD", "a1b2c3d", "test_alpha", "jane", "chevron", "src", "repo"))


def test_the_values_file_holds_each_distinct_value_scrubbed_with_its_kind_count_slots_and_a_few_parts(tmp_path):
    path = corpus(tmp_path)
    written(path, "")
    ids = line_ids(path)
    values = {row["value"]: row for row in map(json.loads, (tmp_path / "values.jsonl").read_text().splitlines())}
    assert {key: values["5"][key] for key in ("kind", "count", "slots", "sample_parts")} == {"kind": "number", "count": 1, "slots": {"git log -n": 1}, "sample_parts": [ids["git log --oneline -n 5 main..HEAD"]]}
    assert {value for value, row in values.items() if "git log argument 1" in row["slots"]} == {"main..HEAD", "a1b2c3d..HEAD", "v1.0..v1.1"}
    assert values["chevron"]["slots"] == {"git log -S": 1}
    assert all(PART_ID.fullmatch(row["id"]) for row in values.values()) and len({row["id"] for row in values.values()}) == len(values)
    assert values["someone@example.com"]["kind"] == "email" and values["~/notes.txt"]["kind"] == "path"
    assert not any(private in text for name, text in outputs(tmp_path).items() if name != path.name for private in ("jane@private.org", "/Users/"))


def test_a_line_the_splitter_splits_wrongly_is_reported_by_its_id_and_check_and_kept_out_of_the_forms(tmp_path):
    path = corpus(tmp_path)
    written(path, "")
    ids = line_ids(path)
    report = dict(row.split("\t", 1) for row in (tmp_path / "splitter-report.txt").read_text().splitlines())
    assert report[ids['echo "unclosed && ls']] == "open at end: part 1 ends inside an open quote"
    assert report[ids["cat <<'EOF' && ls\\nbody\\nEOF"]].startswith("shlex: ")
    assert ids["git status --short | head -3"] not in report
    assert not (tmp_path / "forms" / "echo.json").exists() and not (tmp_path / "forms" / "ls.json").exists()
