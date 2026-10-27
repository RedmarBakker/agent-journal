import json

import pytest

from journal.features.updates.support.no_update_path import NoUpdatePath
from journal.features.updates.support.update_path import UpdatePath


def steps_text(oldest: dict[str, str], no_steps: tuple[str, ...] = ()) -> str:
    return json.dumps({**{version: {"step": True, "oldest": accepted, "reason": "r"} for version, accepted in oldest.items()}, **{version: {"step": False, "reason": "r"} for version in no_steps}})


def test_a_journal_within_reach_goes_straight_to_the_newest_step_up_to_its_target_and_one_newer_than_every_step_stays():
    text = steps_text({"4.60.0": "4.60.0", "4.66.1": "4.63.0", "4.70.0": "4.65.0"})
    assert UpdatePath.planned("4.66.0", "4.70.0", text).versions == ("4.70.0",)
    assert UpdatePath.planned("4.70.0", "4.70.0", text).versions == (), "the newest step installed has nowhere to go"
    assert UpdatePath.planned("4.71.2", "4.71.3", text).versions == (), "a journal newer than every step never goes back"
    assert UpdatePath.planned("4.66.0", "4.66.1", text).versions == ("4.66.1",), "a step newer than the version installed is never on its path"


def test_a_journal_twenty_minors_behind_takes_the_newest_step_each_time_and_routes_around_a_release_that_is_no_step():
    text = steps_text({f"4.{minor}.0": f"4.{max(60, minor - 5)}.0" for minor in range(60, 91) if minor != 85}, no_steps=("4.85.0",))
    assert UpdatePath.planned("4.70.0", "4.90.0", text).versions == ("4.75.0", "4.80.0", "4.84.0", "4.89.0", "4.90.0")


def test_a_gap_no_step_bridges_or_a_version_below_every_step_is_no_path_said_in_words():
    text = steps_text({"4.60.0": "4.60.0", "4.65.0": "4.60.0", "4.80.0": "4.75.0"})
    with pytest.raises(NoUpdatePath, match="no step accepts 4.65.0: the next step, 4.80.0, accepts 4.75.0 and newer"):
        UpdatePath.planned("4.62.0", "4.80.0", text)
    with pytest.raises(NoUpdatePath, match="no step accepts 4.50.0: the next step, 4.60.0, accepts 4.60.0 and newer"):
        UpdatePath.planned("4.50.0", "4.80.0", text)


@pytest.mark.parametrize(("text", "words"), [("", "publishes no update_steps.json"), ("{", "cannot be read"), ('{"4.60.0": {"step": true}}', "cannot be read"), ('{"four": {"step": true, "oldest": "4.60.0"}}', "cannot be read"), ("[]", "cannot be read")])
def test_a_missing_or_malformed_steps_file_is_no_path(text: str, words: str):
    with pytest.raises(NoUpdatePath, match=words):
        UpdatePath.planned("4.66.0", "4.70.0", text)
