"""scripts/corpus_forms.py on a corpus of made-up groups: every line gets an ID kept beside it across runs, each line is split into parts with IDs of their own, the forms name kinds, counts and a few parts and never a literal value, the values file holds each distinct value scrubbed, the chains file joins the parts, and the splitter report names a line split wrongly by the check that found it; a line has the same readable ID on every run and allows only separators, continuations and comments between parts, and no corpus file is written inside the repository but under .journal."""

import json
import re
from pathlib import Path

import pytest

from scripts.corpus_commands import refused_inside_repository
from scripts.corpus_forms import PART_ID, content_id, written
from scripts.splitter_check import gap_faults

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
        "cat <<'EOF' && ls\nbody\nEOF",
    ],
]


def corpus(folder: Path) -> Path:
    path = folder / "commands.txt"
    path.write_text("\n\n".join("\n".join(json.dumps(line) for line in group) for group in GROUPS) + "\n")
    return path


def line_ids() -> dict[str, str]:
    return {line: content_id(line) for group in GROUPS for line in group}


def outputs(folder: Path) -> dict[str, str]:
    return {path.relative_to(folder).as_posix(): path.read_text() for path in sorted(folder.rglob("*")) if path.is_file()}


def chains(folder: Path) -> dict[str, list[str]]:
    return {row["line"]: row["chain"] for row in map(json.loads, (folder / "chains.jsonl").read_text().splitlines())}


def test_every_line_part_and_value_id_is_drawn_from_its_content_the_same_on_every_run_with_no_stored_map(tmp_path):
    path = corpus(tmp_path)
    raw = path.read_text()
    written(path, "")
    first = outputs(tmp_path)
    for output in tmp_path.iterdir():
        if output != path and output.is_file():
            output.unlink()
    written(path, "")
    assert outputs(tmp_path) == first and path.read_text() == raw, "a second run from nothing but the corpus gives the same IDs, and the corpus is never rewritten"
    assert set(chains(tmp_path)) <= set(line_ids().values()), "a line is named by the ID drawn from its text"


def test_a_line_is_split_into_parts_joined_in_the_chains_file_and_a_line_of_one_part_is_its_own_part(tmp_path):
    path = corpus(tmp_path)
    written(path, "")
    ids = line_ids()
    cd, joined, log, piped, head = chains(tmp_path)[ids["cd repo && git log --oneline -n 12 a1b2c3d..HEAD | head -5"]]
    assert (joined, piped) == ("&&", "|") and all(PART_ID.fullmatch(part) for part in (cd, log, head))
    assert ids["git log --oneline -n 3 v1.0..v1.1 2>&1"] not in chains(tmp_path)


def test_the_forms_name_kinds_options_counts_and_a_few_parts_and_hold_no_literal_value(tmp_path):
    path = corpus(tmp_path)
    written(path, "")
    ids = line_ids()
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
    ids = line_ids()
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
    ids = line_ids()
    report = dict(row.split("\t", 1) for row in (tmp_path / "splitter-report.txt").read_text().splitlines())
    assert report[ids['echo "unclosed && ls']] == "open at end: part 1 ends inside an open quote"
    assert report[ids["cat <<'EOF' && ls\nbody\nEOF"]].startswith("shlex: ")
    assert ids["git status --short | head -3"] not in report
    assert not (tmp_path / "forms" / "echo.json").exists() and not (tmp_path / "forms" / "ls.json").exists()


REPOSITORY = Path(__file__).resolve().parents[1]


def test_a_line_keeps_its_readable_id_on_every_run_with_no_stored_map():
    first, again, other = content_id("git status && git diff"), content_id("git status && git diff"), content_id("git status")
    assert first == again != other and len(first) == 19 and first.count("-") == 3, first


def test_only_space_separators_continuations_and_comments_lie_between_parts():
    assert gap_faults("cd x\n# a comment\nawk a; \\\nls && b &") == []
    assert gap_faults("echo a; echo b") == []


def test_no_corpus_file_is_written_inside_the_repository():
    with pytest.raises(SystemExit, match="never enters the repository"):
        refused_inside_repository(REPOSITORY / "tests" / "corpus.txt")
    refused_inside_repository(REPOSITORY / ".journal" / "corpus" / "commands.txt")


FIXTURES = ["splitter/*", "shell_corpus.jsonl", "hydration_corpus.jsonl", "commands/*", "shell_corpus_reading/*", "generated/*"]
HOME_FOLDER = re.compile(r"[/-](?:Users|home)[/-](?!(?:me|user)\b)[A-Za-z0-9_.]+")
EMAIL = re.compile(r"[\w.%+-]+@((?:[\w-]+\.)+[A-Za-z]{2,})\b")
STAND_IN_DOMAINS = re.compile(r"(?:^|\.)example\.(?:com|org|net)$|^github\.com$|\.(?:forest|turtle|valley)$", re.I)
# the machine's host name is a private word too, when it is long enough not to be a common word; the user's name is not, being the public
# owner of the repository and its packages
MACHINE_NAME_MINIMUM = 4
KEY = re.compile(r"(?<![\w/+=-])(?=[A-Za-z0-9+]*[a-z])(?=[A-Za-z0-9+]*[A-Z])(?=[A-Za-z0-9+]*\d)[A-Za-z0-9+]{32,}={0,2}(?![\w/+=-])")


def test_no_fixture_holds_a_home_folder_an_email_a_real_address_a_key_or_a_private_word():
    import importlib.util
    spec = importlib.util.spec_from_file_location("private_data", REPOSITORY / "scripts" / "checks" / "private_data.py")
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    import socket
    words = [line.strip().lower() for line in guard.WORDS.read_text().splitlines() if line.strip()] if guard.WORDS.is_file() else []
    words += [name for name in [socket.gethostname().split(".")[0].lower()] if len(name) > MACHINE_NAME_MINIMUM]
    found = []
    for path in sorted(file for pattern in FIXTURES for file in (REPOSITORY / "tests").glob(pattern) if file.is_file()):
        text = path.read_text(errors="replace")
        lowered = text.lower()
        found += [f"{path.name}: home folder {home}" for home in sorted(set(HOME_FOLDER.findall(text)))]
        found += [f"{path.name}: email at {domain}" for domain in sorted(set(EMAIL.findall(text))) if not STAND_IN_DOMAINS.search(domain)]
        found += [f"{path.name}: the address {address}" for address in sorted(set(guard.ADDRESS.findall(text))) if guard.is_public(address)]
        found += [f"{path.name}: a key of {len(key)} characters" for key in sorted(set(KEY.findall(text)))]
        found += [f"{path.name}: private word {index}" for index, word in enumerate(words, 1) if word in lowered]
    assert found == [], found[:20]


REGENERATE = "PYTHONPATH=src python3 -m scripts.splitter_fixture .journal/corpus"


def test_the_committed_splitter_fixture_holds_every_line_the_generator_makes_without_a_corpus():
    from scripts.splitter_fixture import FIXTURE, compound_lines, row
    committed = {json.loads(line)["line"]: json.loads(line)["parts"] for line in FIXTURE.read_text().splitlines()}
    generated = {line: row(line)["parts"] for line in compound_lines()}
    assert not [line for line in generated if line not in committed], f"the generator makes lines the fixture lacks: regenerate it with {REGENERATE}"
    assert not [line for line, parts in generated.items() if committed[line] != parts], f"Chain or Part changed since the fixture was made: regenerate it with {REGENERATE}"


def test_a_generated_line_holds_only_generated_values_and_a_program_one_project_ran_is_left_out(tmp_path):
    from scripts.splitter_fixture import VALUES, filled, form_lines, seeded
    form = "git log [--oneline] [-n <number>] [<range>] <path>"
    words = set(filled(form, seeded(form)).split()) - set(form.replace("[", " ").replace("]", " ").split())
    assert words and words <= {value for pool in VALUES.values() for value in pool}, "every value is drawn from the pools, never from the corpus"
    (tmp_path / "git.json").write_text(json.dumps({"program": "git", "subcommands": {"log": {"parts": 3, "forms": [{"form": form, "seen": 3}]}}}))
    assert form_lines(tmp_path, {"git": 1, "git log": 1}) == [], "a program one project ran never ships"
    assert form_lines(tmp_path, {"git": 3, "git log": 1}) == [], "a subcommand one project ran never ships"
    assert len(form_lines(tmp_path, {"git": 3, "git log": 3})) == 1


def test_the_generated_forms_fixture_keeps_only_forms_several_projects_ran_and_chains_of_plain_operators(tmp_path, monkeypatch):
    import scripts.generated_forms as generated_forms
    corpus_folder = tmp_path / "corpus"
    (corpus_folder / "forms").mkdir(parents=True)
    form = "git log [--oneline] [-n <number>]"
    (corpus_folder / "forms" / "git.json").write_text(json.dumps({"program": "git", "subcommands": {"log": {"parts": 3, "forms": [{"form": form, "seen": 3}]}, "secret": {"parts": 9, "forms": [{"form": "git secret", "seen": 9}]}}}))
    (corpus_folder / "projects.json").write_text(json.dumps({"git": 3, "git log": 3, "git secret": 1}))
    (corpus_folder / "chains.jsonl").write_text("".join(json.dumps({"chain": chain}) + "\n" for chain in (["abcd-efgh-ijkm-npqr", "&&", "stuv-wxyz-2345-6789"], ["abcd-efgh-ijkm-npqr", ">", "out"])))
    monkeypatch.setattr(generated_forms, "FIXTURE", tmp_path / "forms.json")
    generated_forms.main(corpus_folder)
    written = json.loads((tmp_path / "forms.json").read_text())
    assert written["forms"] == [{"program": "git", "subcommand": "log", "form": form}], "a subcommand one project ran never ships"
    assert written["chains"] == [["PART", "&&", "PART"]], "a chain joined by anything but &&, ;, |, || or 2>&1 is left out"
