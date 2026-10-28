from tests.scenarios.builder.path_overlay import PathOverlay


def test_overlapping_stories_fail_the_overlay():
    overlay = PathOverlay()
    overlay.add("test_long", ["agent runs task pause", "working > following_plan on task_paused", "agent runs task create", "agent stops", "said tasks.carry_on"])
    overlay.add("test_longer", ["agent runs task pause", "working > following_plan on task_paused", "agent runs task create", "agent stops", "said tasks.carry_on", "agent runs task complete"])
    overlay.add("test_other", ["agent runs message read", "said messages.answer_the_message_read"])
    failures = overlay.failures()
    assert any(line.startswith("test_long reaches nothing the other scenarios do not") for line in failures), failures
    assert any("test_long and test_longer share 82% of their path, the same for their first 5 steps" in line for line in failures), failures
    assert not any("test_other" in line for line in failures), "a story on a path of its own passes"
