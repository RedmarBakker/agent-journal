import pytest

from tests.agent_hooks import typing_capture, pinned_clock, story_seconds
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
    pinned = story_seconds(app)
    seeded = Story(app, VoidProvider, SettingReads(), copies, monkeypatch)
    seeded.reach(StartedTask)
    reached = (seeded.tasks.started, seeded.stack(), seeded.api_row("tasks", seeded.tasks.started)["state"])
    assert {(NewSession, VoidProvider.name), (WorkingAgent, VoidProvider.name), (StartedTask, VoidProvider.name)} <= set(copies.copies), "the fixture and each one it builds on are kept, for every story of the process"

    copied = Story(app, VoidProvider, SettingReads(), copies, monkeypatch)
    copied.reach(StartedTask)
    assert (copied.tasks.started, copied.stack(), copied.api_row("tasks", copied.tasks.started)["state"]) == reached, "a story from the copy starts from the rows and the stack the seeder reached"
    assert story_seconds(app) == pinned, "restoring a fixture preserves the story's pinned clock"


def test_story_time_travel_advances_from_its_pinned_time_when_the_clock_is_ahead(app, monkeypatch, copies):
    typing_capture(app, monkeypatch, [])
    pinned_clock(app, monkeypatch)
    story = Story(app, VoidProvider, SettingReads(), copies, monkeypatch)
    source = app.container.get(TimeSource)
    clock = app.container.get(Clock)
    pinned = source.seconds()
    clock.held_at += 41

    story.time_travel(seconds=120)

    assert source.seconds() == pinned + 120, "time travel advances the pinned story time, not real time accumulated in Clock.held_at"
    assert clock.held_at == pinned + 120, "the engine clock follows the pinned story time"


def test_story_seconds_requires_the_pinned_story_clock(app, monkeypatch):
    pinned_clock(app, monkeypatch)
    app.container.get(TimeSource).unpin()

    with pytest.raises(AssertionError, match="story clock is not pinned"):
        story_seconds(app)
