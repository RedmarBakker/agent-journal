import importlib.util
import json
from pathlib import Path

from journal.features.updates.support.update_window import UpdateWindow
from tests.update_matrix_run import PASSED_FILE, STEPS_FILE, WINDOW, pairs, passed_pairs, step
from tests.update_release import PASSED_REASON, SKIPPED_REASON, UpdateRelease


def test_the_update_matrix_tests_each_release_only_from_the_releases_of_the_five_minors_before_it():
    tags = ["v4.60.0", "v4.61.0", "v4.63.0", "v4.63.1", "v4.67.0", "v4.68.0", "v4.68.1"]
    kept = pairs(UpdateWindow(5), tags, "4.69.0", {"v4.60.0 v4.61.0"})
    assert kept == [
        ("v4.60.0", "v4.63.0"), ("v4.60.0", "v4.63.1"),
        ("v4.61.0", "v4.63.0"), ("v4.61.0", "v4.63.1"),
        ("v4.63.0", "v4.63.1"), ("v4.63.0", "v4.67.0"), ("v4.63.0", "v4.68.0"), ("v4.63.0", "v4.68.1"),
        ("v4.63.1", "v4.67.0"), ("v4.63.1", "v4.68.0"), ("v4.63.1", "v4.68.1"),
        ("v4.67.0", "v4.68.0"), ("v4.67.0", "v4.68.1"), ("v4.67.0", "tree"),
        ("v4.68.0", "v4.68.1"), ("v4.68.0", "tree"),
        ("v4.68.1", "tree"),
    ], "a start is kept only for targets at most five minors on, patches with their minor, across the gap from 4.63 to 4.67, less the pairs that passed"
    assert pairs(UpdateWindow(5), ["v4.68.0", "v5.0.0"], "5.0.0", set()) == [("v5.0.0", "tree")], "a new major starts a window of its own"


TAGS = ["v4.61.0", "v4.62.0", "v4.62.1", "v4.66.0"]


def suite_script():
    spec = importlib.util.spec_from_file_location("suite", Path(__file__).resolve().parents[1] / "scripts" / "suite.py")
    suite = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(suite)
    return suite


def test_a_release_run_that_passed_keeps_the_trees_pairs_under_its_version_and_writes_it_as_a_step(tmp_path: Path):
    release = UpdateRelease("4.67.0", TAGS, UpdateWindow(5), tmp_path / "passed.json", tmp_path / "steps.json")
    release.passed()
    assert json.loads(release.passed_file.read_text()) == ["v4.62.0 v4.67.0", "v4.62.1 v4.67.0", "v4.66.0 v4.67.0"], "the tree's pairs are kept under the version it is about to become, 4.61 outside the window"
    assert json.loads(release.steps_file.read_text()) == {"4.67.0": {"step": True, "oldest": "4.62.0", "reason": PASSED_REASON}}, "it is a step from the oldest release of its window"


def test_a_version_missing_one_pair_of_its_window_is_no_step():
    passed = {"v4.62.0 v4.67.0", "v4.66.0 v4.67.0"}
    assert step(UpdateWindow(5), TAGS, "4.67.0", passed, PASSED_REASON) == {"step": False, "reason": "the update from v4.62.1 to it never passed"}


def test_a_skipped_release_run_writes_its_version_as_no_step(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("JOURNAL_SKIP_UPDATE_MATRIX", "1")
    release = UpdateRelease("4.67.0", TAGS, UpdateWindow(5), tmp_path / "passed.json", tmp_path / "steps.json")
    assert suite_script().update_matrix(release) == 0
    assert json.loads(release.steps_file.read_text()) == {"4.67.0": {"step": False, "reason": SKIPPED_REASON}}
    assert not release.passed_file.exists(), "a skipped run keeps no pair"


def test_a_release_run_of_a_version_tagged_already_is_refused_and_writes_nothing(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("JOURNAL_SKIP_UPDATE_MATRIX", raising=False)
    release = UpdateRelease("4.66.0", TAGS, UpdateWindow(5), tmp_path / "passed.json", tmp_path / "steps.json")
    assert suite_script().update_matrix(release) == 1
    assert not release.steps_file.exists() and not release.passed_file.exists()


def test_every_step_of_the_first_steps_file_is_proven_by_the_passed_pairs():
    steps, passed = json.loads(STEPS_FILE.read_text()), passed_pairs(PASSED_FILE)
    assert steps["4.60.0"]["oldest"] == "4.60.0", "the first release accepts only itself"
    for at, (version, entry) in enumerate(steps.items()):
        earlier = [f"v{older}" for older in list(steps)[:at]]
        assert step(WINDOW, earlier, version, passed, str(entry["reason"])) == entry, f"{version} is the step its window's passed pairs make it"
