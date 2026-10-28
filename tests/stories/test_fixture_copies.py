from tests.replay import typing_capture, pinned_clock
from tests.stories.builder.story import Story
from tests.stories.builder.setting_reads import SettingReads
from tests.stories.builder.void_provider import VoidProvider
from tests.stories.fixtures.working_agent import WorkingAgent
from tests.stories.fixtures.started_task import StartedTask


def test_a_fixture_is_seeded_once_and_its_copy_is_the_state_the_seeder_reached(app, journal, monkeypatch, copies):
    typing_capture(app, monkeypatch, [])
    pinned_clock(app, monkeypatch)
    seeded = Story(app, VoidProvider, SettingReads(), copies)
    seeded.reach(StartedTask)
    reached = (seeded.start.started_task, seeded.stack(), seeded.api_row("tasks", seeded.start.started_task)["state"])
    assert set(copies.copies) == {(WorkingAgent, VoidProvider.name), (StartedTask, VoidProvider.name)}, "the fixture and the one it builds on are each kept once"

    journal.reset()
    copied = Story(app, VoidProvider, SettingReads(), copies)
    copied.reach(StartedTask)
    assert (copied.start.started_task, copied.stack(), copied.api_row("tasks", copied.start.started_task)["state"]) == reached, "a story from the copy starts from the rows and the stack the seeder reached"
