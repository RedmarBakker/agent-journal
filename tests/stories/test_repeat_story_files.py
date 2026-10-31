from importlib import import_module

import pytest

from journal.support.listener_queue import ListenerQueue
from tests.agent_hooks import pinned_clock, typing_capture
from tests.stories.builder.setting_reads import SettingReads
from tests.stories.builder.story import Story
from tests.stories.builder.story_marks import PROVIDER_MARK, SETTINGS_MARK, START_MARK
from tests.stories.builder.void_provider import VoidProvider
from tests.stories.conftest import home_inside_the_story_folder
from tests.stories.fixtures.main.started_plan import StartedPlan

FILES = (
    "tests.stories.main.plans.dependency_readiness",
    "tests.stories.main.organization.role_handoff_requires_clock_out",
    "tests.stories.main.tasks.task_blocks",
    "tests.stories.worker.tests.queued_clock_outs",
)


def marked_stories():
    for file in FILES:
        module = import_module(file)
        for name, function in vars(module).items():
            if name.startswith("test_") and callable(function):
                marks = function.pytestmark if isinstance(function.pytestmark, list) else [function.pytestmark]
                yield name, function, marks


def play_story(app, copies, function, marks, monkeypatch):
    home_inside_the_story_folder(app.config.root, monkeypatch)
    typed = []
    typing_capture(app, monkeypatch, typed)
    pinned_clock(app, monkeypatch)
    reads = SettingReads()
    reads.watch(monkeypatch)
    provider = next((mark.args[0] for mark in marks if mark.name == PROVIDER_MARK), VoidProvider)
    story = Story(app, provider, reads, copies, monkeypatch)
    story.typed = typed
    fixture, mode, subject = next(mark.args for mark in marks if mark.name == START_MARK)
    story.reach(fixture)
    story.plays_in(mode)
    story.scope = subject
    for mark in marks:
        if mark.name == SETTINGS_MARK:
            story.user_sets(*mark.args)
    try:
        function(story)
    except AssertionError as failure:
        raise AssertionError(
            f"{failure}; stack={story.stack()}, queue={app.container.get(ListenerQueue).depth()}"
        ) from failure
    for close in story.closers:
        close()
    story.drain_seat_runner()
    app.container.get(ListenerQueue).drain()
    assert story.is_stack_checked_last(), f"{function.__name__} did not end with a checked stack"
    assert not story.fixture.unused_rows(), f"{function.__name__} left fixture rows unused"
    assert not story.unread_settings(), f"{function.__name__} left settings unread: {story.unread_settings()}"
    return story


def test_a_task_block_story_restores_its_started_plan_on_every_repeat(app, copies):
    stories = [story for story in marked_stories()
               if story[1].__module__ == "tests.stories.main.tasks.task_blocks"]
    target = next(index for index, story in enumerate(stories)
                  if story[0] == "test_a_task_waits_for_the_whole_plan_and_opens_when_it_finishes")
    for _, function, marks in stories[:target]:
        with pytest.MonkeyPatch.context() as monkeypatch:
            play_story(app, copies, function, marks, monkeypatch)
    _, function, marks = stories[target]
    for repeat in range(10):
        with pytest.MonkeyPatch.context() as monkeypatch:
            try:
                played = play_story(app, copies, function, marks, monkeypatch)
                if repeat == 0:
                    seeded = copies.copies[(StartedPlan, VoidProvider.name)].journal.rows
                    task_states = [row[0] for row in seeded.execute("select state from tasks order by id")]
                    plan_state = seeded.execute("select state from plans where id = 1").fetchone()[0]
                    assert task_states == ["started", "open"], f"the seeder copy holds task states {task_states} after its story ran"
                    assert plan_state == "started", f"the seeder copy's plan is {plan_state} after its story ran"
            except AssertionError as failure:
                raise AssertionError(f"repeat {repeat}: {failure}") from failure
