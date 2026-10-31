from tests.agent_hooks import typing_capture, pinned_clock
from tests.stories.builder.story import Story
from tests.stories.builder.setting_reads import SettingReads
from tests.stories.builder.void_provider import VoidProvider
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.main.started_task import StartedTask
from journal.engine.clock import Clock
from journal.support.time_source import TimeSource


def test_story_journal_stops_scheduled_jobs_so_time_moves_only_in_story_steps(journal):
    assert journal.app.runtime().jobs._thread is None, "a background tick cannot race a story's clock steps"


def test_a_fixture_is_seeded_once_and_its_copy_is_the_state_the_seeder_reached(app, journal, monkeypatch, copies):
    typing_capture(app, monkeypatch, [])
    pinned_clock(app, monkeypatch)
    pinned_at = app.container.get(TimeSource).pinned_seconds
    seeded = Story(app, VoidProvider, SettingReads(), copies, monkeypatch)
    seeded.reach(StartedTask)
    reached = (seeded.tasks.started, seeded.stack(), seeded.api_row("tasks", seeded.tasks.started)["state"])
    assert {(NewSession, VoidProvider.name), (WorkingAgent, VoidProvider.name), (StartedTask, VoidProvider.name)} <= set(copies.copies), "the fixture and each one it builds on are kept, for every story of the process"

    journal.reset()
    assert app.container.get(TimeSource).pinned_seconds is None, "the shared journal reset restores its boot clock"
    current_story_time = pinned_at + 123
    app.container.get(Clock).held_at = current_story_time
    app.container.get(TimeSource).pin(current_story_time)
    copied = Story(app, VoidProvider, SettingReads(), copies, monkeypatch)
    copied.reach(StartedTask)
    assert (copied.tasks.started, copied.stack(), copied.api_row("tasks", copied.tasks.started)["state"]) == reached, "a story from the copy starts from the rows and the stack the seeder reached"
    assert app.container.get(Clock).held_at == current_story_time, "restoring the fixture keeps the current story clock"
    assert app.container.get(TimeSource).pinned_seconds == current_story_time, "restoring the fixture keeps the current story clock"
