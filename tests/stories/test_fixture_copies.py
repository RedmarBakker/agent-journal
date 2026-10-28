from tests.replay import catch_typed, drive_the_clock
from tests.stories.builder.story import Story
from tests.stories.builder.setting_reads import SettingReads
from tests.stories.builder.void_provider import VoidProvider
from tests.stories.fixtures.agent_at_work import AgentAtWork
from tests.stories.fixtures.task_in_hand import TaskInHand


def test_a_fixture_is_seeded_once_and_its_copy_is_the_state_the_seeder_reached(app, journal, monkeypatch, copies):
    catch_typed(app, monkeypatch, [])
    drive_the_clock(app, monkeypatch)
    seeded = Story(app, VoidProvider, SettingReads(), copies)
    seeded.starts_from(TaskInHand)
    reached = (seeded.start.task_in_hand, seeded.stack(), seeded.api_row("tasks", seeded.start.task_in_hand)["state"])
    assert set(copies.copies) == {(AgentAtWork, VoidProvider.name), (TaskInHand, VoidProvider.name)}, "the fixture and the one it builds on are each kept once"

    journal.reset()
    copied = Story(app, VoidProvider, SettingReads(), copies)
    copied.starts_from(TaskInHand)
    assert (copied.start.task_in_hand, copied.stack(), copied.api_row("tasks", copied.start.task_in_hand)["state"]) == reached, "a story from the copy starts from the rows and the stack the seeder reached"
