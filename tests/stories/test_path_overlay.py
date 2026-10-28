from tests.stories.builder.path_overlay import PathOverlay


def test_overlapping_stories_fail_the_overlay():
    overlay = PathOverlay()
    overlay.add("test_long", ["agent runs task pause", "working > following_plan on task_paused", "agent runs task create", "agent stops", "said tasks.carry_on"])
    overlay.add("test_longer", ["agent runs task pause", "working > following_plan on task_paused", "agent runs task create", "agent stops", "said tasks.carry_on", "agent runs task complete"])
    overlay.add("test_other", ["agent runs message read", "said messages.answer_the_message_read"])
    failures = overlay.failures()
    assert any(line.startswith("test_long reaches nothing the other stories do not") for line in failures), failures
    assert any("test_long and test_longer share 82% of their path, the same for their first 5 steps" in line for line in failures), failures
    assert not any("test_other" in line for line in failures), "a story on a path of its own passes"


def test_stories_opening_with_the_same_steps_are_told_to_share_a_fixture():
    overlay = PathOverlay()
    opening = ["starts from StartedTask", "agent runs task create", "agent runs task complete", "agent stops, refused"]
    overlay.add("test_auto_on", [*opening, "said tasks.carry_on"])
    overlay.add("test_auto_off", [*opening[:3], "agent stops, let through"])
    overlay.add("test_elsewhere", ["starts from WorkingAgent", "agent runs task create", "agent runs task complete", "agent stops, refused"])
    failures = overlay.failures()
    assert not any("open with" in line for line in failures), "two steps alike are no shared opening"
    overlay.add("test_auto_off", [*opening[:4], "agent writes"])
    failures = overlay.failures()
    assert any(line.startswith("test_auto_off and test_auto_on open with the same 3 steps") for line in failures), failures
    assert not any("test_elsewhere" in line and "open with" in line for line in failures), "the same steps from another fixture are no shared opening"
