from tests.scenarios.builder.path_overlay import PathOverlay


def test_two_stories_walking_one_path_fail_naming_where_they_part_and_a_story_reaching_nothing_of_its_own_fails_too():
    overlay = PathOverlay()
    overlay.add("test_long", ["agent runs task pause", "working > following_plan on task_paused", "agent runs task create", "agent stops", "said tasks.carry_on"])
    overlay.add("test_longer", ["agent runs task pause", "working > following_plan on task_paused", "agent runs task create", "agent stops", "said tasks.carry_on", "agent runs task complete"])
    overlay.add("test_other", ["agent runs message read", "said messages.answer_the_message_read"])
    failures = overlay.failures()
    assert any(line.startswith("test_long reaches nothing the other scenarios do not") for line in failures), failures
    assert any("test_long and test_longer share 83% of their path, the same for their first 5 steps" in line for line in failures), failures
    assert not any("test_other" in line for line in failures), "a story on a path of its own passes"
