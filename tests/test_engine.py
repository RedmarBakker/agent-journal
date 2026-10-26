"""Phase five: the machine. A write in Idle is refused with how to declare work; after task start a stop says carry on, once; done makes the agent idle again; stuck pauses and a tool use lifts it; the state survives a new server."""

import re
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request as HttpRequest, urlopen
from journal.support.timeout import Timeout
from journal.repositories.reports import Reports
from journal.events.rows.worker_mention import WorkerMention

import pytest

from journal.providers.claude import Claude
from journal.support.tool_call import ToolCall

shell = lambda line: Claude().call("Bash", {"command": line}, frozenset())

from journal.app import App
from journal.engine.support.session_agents import SessionAgents
from journal.config import Config
from journal.support.moment import Moment
from journal.support.caller import Caller
from journal.engine.hook_answer import HookAnswer
from journal.engine.state_machine import StateMachine
from journal.features.tasks.states.impasse import Impasse
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.agent import Agent
from journal.models.setting import Setting
from journal.db.migrations.stack_seed import StackSeed
from journal.repositories.agents import Agents
from journal.repositories.plans import Plans
from journal.repositories.tasks import Tasks
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.models.task import Task
from journal.events.listener import Listener
from journal.engine.job import Job
from journal.events.bus import Bus
from journal.events.rows.plan_started import PlanStarted
from journal.events.rows.row_event import RowEvent
from journal.events.rows.row_resolved import RowResolved
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_logged import TaskLogged
from journal.events.rows.task_started import TaskStarted
from journal.events.rows.question_answered import QuestionAnswered
from journal.events.rows.worker_reported import WorkerReported
from journal.events.models.updated import Updated
from journal.engine.row_event_delivery import RowEventDelivery
from journal.models.question import Question
from journal.models.task_log import TaskLog
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from datetime import datetime, timezone
from journal.repositories.entries import Entries
from journal.http.agents.agent_activity import AgentActivity
from journal.engine.support.stack_history import StackHistory
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.repositories.setting_rows import SettingRows
from dataclasses import dataclass, replace

from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.states.wait import Wait
from journal.engine.support.block import Block
from journal.events.feature_data import FeatureData
from journal.support.rejection import Rejection
from journal.engine.nudge import Nudge
from journal.engine.states.compacting import Compacting as CompactingState
from journal.engine.states.ended import Ended
from journal.features.registry import Registry
from journal.engine.support.data_readers import DataReaders
from journal.features.messages.feature import Messages as MessagesFeature
from journal.features.briefing.feature import Briefing as BriefingFeature
from journal.features.workers.feature import Workers as WorkersFeature
from journal.engine.nudger import Nudger
from journal.engine.nudge_registry import NudgeRegistry
from journal.support.time_source import TimeSource
from journal.events.agent.session_started import SessionStarted
from tests.in_process import posted
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.stop import Stop
from journal.engine.states.wait import Wait
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.compacting import Compacting
from journal.events.agent.session_ended import SessionEnded
from journal.events.agent.ticked import Ticked
from journal.events.agent.tool_starting import ToolStarting
from journal.events.event import Event
from journal.support.option import Option
from journal.engine.support.settings import Settings as SettingsValue
from journal.engine.support.stack import Stack
from journal.engine.support.typist import Typist
from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.transition import Transition
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.shell.shell_part import ShellPart
from journal.features.tasks.tasks_part import TasksPart
from journal.features.etiquette.etiquette_options import EtiquetteOptions
from journal.features.messages.messages_options import MessagesOptions
from journal.features.workers.workers_options import WorkersOptions
from journal.features.workers.workers_nudges import WorkersNudges

AGENT = Caller.agent("main", "s1", "claude")
USER = Caller.user("main")


@pytest.fixture(scope="module")
def boot():
    def booted(root: Path, patch: pytest.MonkeyPatch) -> App:
        app = App(Config(root, port=0))
        app.container.get(SettingRows).save(Setting(environment_id=0, key="features.skills", value=False), Actor.system())
        app.runtime().start()
        return app
    return booted


def hook(app, kind: str, **body):
    return posted(app, "/hooks/claude", {"hook_event_name": kind, "session_id": "s1", **body}, {"X-Journal-Env": "main"})


def write(app):
    return hook(app, "PreToolUse", tool_name="Write", tool_input={"file_path": "a.py"})


def test_task_start_moves_the_agent_to_working_and_every_stop_says_carry_on(app: App):
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    app.console().run(["task", "create", "ship it", "--start"], AGENT)
    assert app.container.get(SessionAgents).top("s1").task_id == 1
    assert write(app)[0] == 200
    status, body = hook(app, "Stop")
    assert body.get("decision") == "block" and "task 1 is in hand, last logged just now: carry on" in body["reason"], "a stop with work in hand is held, which is how Claude is told to go on"
    assert hook(app, "Stop")[1].get("decision") == "block", "every fresh stop with work in hand is held, until a stuck"
    assert hook(app, "PreCompact")[1] == {}, "a compaction hook carries nothing to the agent; the marks said it"


def test_done_makes_the_agent_idle_again(app: App):
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    app.console().run(["task", "create", "t", "--start"], AGENT)
    app.console().run(["task", "complete", "1"], AGENT)
    assert isinstance(app.container.get(SessionAgents).top("s1"), Ready)
    assert hook(app, "Stop")[1] == {}


def test_stuck_pauses_and_the_next_tool_use_goes_back_to_where_it_was(app: App):
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    app.console().run(["task", "create", "t", "--start"], AGENT)
    app.console().run(["stuck", "stuck on the login"], AGENT)
    machine = app.container.get(StateMachine)
    assert isinstance(app.container.get(SessionAgents).top("s1"), Impasse) and app.container.get(SessionAgents).top("s1").reason == "stuck on the login"
    assert hook(app, "Stop")[1] == {}
    hook(app, "PreToolUse", tool_name="Read", tool_input={})
    assert app.container.get(SessionAgents).top("s1").task_id == 1


def test_a_feature_switched_off_takes_its_gate_with_it(app: App):
    app.container.get(SettingRows).save(Setting(environment_id=0, key="features.tasks", value=False), Actor.user(1))
    app.console().run(["task", "create", "t", "--start"], AGENT)
    assert hook(app, "Stop")[1] == {}


def test_the_session_end_ends_the_agent_and_a_new_start_of_the_same_session_revives_it(app: App):
    hook(app, "SessionStart")
    hook(app, "SessionEnd")
    assert app.container.get(SessionAgents).top("s1").name == "ended"
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    assert app.container.get(SessionAgents).top("s1").name == "idle"


def test_the_state_is_in_the_database_so_a_new_server_finds_it(tmp_path):
    first = App(Config(tmp_path, port=0))
    first.container.get(SettingRows).save(Setting(environment_id=0, key="features.skills", value=False), Actor.system())
    first.runtime().start()
    hook(first, "SessionStart")
    first.console().run(["environment", "overview"], AGENT)
    first.console().run(["task", "create", "t", "--start"], AGENT)
    first.runtime().stop()
    second = App(Config(tmp_path, port=0))
    second.runtime().start()
    try:
        assert second.container.get(SessionAgents).top("s1").task_id == 1
        assert write(second)[0] == 200
    finally:
        second.runtime().stop()


def test_a_tick_reaches_the_machine_without_a_hook(app: App):
    from journal.engine.clock import Clock
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    app.container.get(Clock).tick(app.container.get(Clock).time())
    assert isinstance(app.container.get(SessionAgents).top("s1"), Ready)


class Counting(Job):
    """A job that notes the time of each of its ticks."""

    def __init__(self, interval_seconds: float) -> None:
        self.interval_seconds, self.ticks = interval_seconds, []

    def tick(self, time: float) -> None:
        self.ticks.append(time)


class Failing(Counting):
    def tick(self, time: float) -> None:
        super().tick(time)
        raise RuntimeError("a tick that fails")


def test_the_job_runner_ticks_each_job_at_its_own_interval_on_a_driven_clock(app: App):
    from journal.engine.clock import Clock
    from journal.engine.job_runner import JobRunner
    runner = JobRunner(app.container.get(Clock), Bus())
    every_second, every_three_seconds, failing = Counting(1.0), Counting(3.0), Failing(2.0)
    for job in (every_second, every_three_seconds, failing):
        runner.register(job)
    waits = [runner.run_due(float(second)) for second in range(10)]
    assert every_second.ticks == [float(second) for second in range(1, 10)], "a job is first due one interval after the runner sees it"
    assert every_three_seconds.ticks == [3.0, 6.0, 9.0], "each job at its own interval"
    assert failing.ticks == [2.0, 4.0, 6.0, 8.0], "a job that raises is logged and ticked again at its next turn"
    assert waits == [1.0] * 10, "the runner sleeps until the next job is due"


def test_a_timeout_is_started_at_a_moment_asked_at_a_later_one_and_kept_by_a_state_through_its_row():
    from journal.features.tasks.states.external_wait import ExternalWait
    from journal.support.timeout import Timeout
    reminder = Timeout.minutes(15).started(100.0)
    assert not reminder.is_elapsed(999.0) and reminder.is_elapsed(1000.0), "fifteen minutes after the time it was started at"
    assert not reminder.started(1000.0).is_elapsed(1899.0), "reset by a later moment, it counts from there"
    assert Timeout.seconds(30).started(5.0).is_elapsed(35.0) and not Timeout.seconds(30).started(5.0).is_elapsed(34.0)
    assert Timeout.tool_uses(25).started(10).is_elapsed(35) and not Timeout.tool_uses(25).started(10).is_elapsed(34), "a count of tool uses"
    assert Timeout.marks(1).started(2).is_elapsed(3) and not Timeout.marks(1).started(2).is_elapsed(2), "a count of context marks"
    waiting = ExternalWait.opened("the build", "checks:2", 100.0)
    assert ExternalWait.restored(json.loads(json.dumps(waiting.serialized()))) == waiting, "a state keeps its timeouts through the json on its row"


def test_one_task_in_hand_pause_resume_and_await(app: App):
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    console = app.console()
    console.run(["task", "create", "first", "--start"], AGENT)
    console.run(["task", "create", "second"], AGENT)
    refused = console.run(["task", "start", "2"], AGENT)
    assert refused.code == 1 and "task 1 is in hand" in refused.error
    console.run(["task", "pause", "1", "waiting for the designer"], AGENT)
    assert isinstance(app.container.get(SessionAgents).top("s1"), Ready), "paused: nothing in hand"
    assert console.run(["task", "resume", "1"], AGENT).code == 0 and app.container.get(SessionAgents).top("s1").task_id == 1
    assert console.run(["await", "the deploy to finish", "--until", "false"], AGENT).code == 0
    stopped = hook(app, "Stop")[1]
    assert app.container.get(SessionAgents).top("s1").name == "awaiting" and stopped.get("decision") == "block" and "task 2 is open" in stopped["reason"], "a stop while waiting on what it cannot estimate is refused while task 2 is open"
    hook(app, "PreToolUse", tool_name="Read", tool_input={})
    assert app.container.get(SessionAgents).top("s1").task_id == 1, "working again lifts the wait"


def test_edits_with_nothing_logged_are_asked_named_and_held_as_the_settings_say(app: App):
    from journal.support.actor import Actor
    from journal.models.setting import Setting
    for key, value in (("tasks.first_nudge_after", 5), ("tasks.name_every", 10), ("tasks.log_after", 20)):
        app.container.get(SettingRows).save(Setting(environment_id=0, key=key, value=value), Actor.system())
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    app.console().run(["task", "create", "t", "--start"], AGENT)
    answers = [write(app) for _ in range(21)]
    assert all(status == 200 for status, _ in answers[:20])
    assert "5 edits since you logged task 1: say where it stands" in json.dumps(answers[5][1]) and "logged" not in json.dumps(answers[4][1]), "the first ask after five"
    assert "task 1 in hand, 10 edits" in json.dumps(answers[10][1]), "named back every ten"
    assert answers[20][0] == 409 and "20 edits since you logged task 1" in answers[20][1]["error"]
    assert all(status == 200 for status, _ in [hook(app, "PreToolUse", tool_name="Read", tool_input={}) for _ in range(3)]), "a read is never held for a log"
    app.console().run(["task", "log", "1", "halfway"], AGENT)
    assert write(app)[0] == 200


def test_every_stop_with_a_task_in_hand_says_carry_on_and_stuck_is_the_way_out(app: App):
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    app.console().run(["task", "create", "t", "--start"], AGENT)
    answers = [hook(app, "Stop", stop_hook_active=i > 0) for i in range(4)]
    assert all(item[1].get("decision") == "block" and "task 1 is in hand, last logged just now: carry on" in item[1]["reason"] for item in answers), "there is no repeated-stop escape"
    hook(app, "PreToolUse", tool_name="Bash", tool_input={"command": "journal stuck 'I cannot reach the service'"})
    app.console().run(["stuck", "I cannot reach the service"], AGENT)
    assert hook(app, "Stop")[1] == {}, "stuck lets the agent stop"
def test_a_blocked_task_waits_on_something_outside_and_is_neither_offered_nor_nudged(app: App):
    from journal.models.task_state import TaskState
    from journal.repositories.tasks import Tasks
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], AGENT)
    console.run(["task", "create", "the tree"], AGENT)
    assert "waiting on: the payment sandbox coming back" in console.run(["task", "block", "1", "the payment sandbox coming back"], AGENT).text
    assert app.container.get(Tasks).find(1).state == TaskState.BLOCKED and app.container.get(SessionAgents).top("s1").name == "idle"
    assert "tasks 1 are blocked" in hook(app, "Stop")[1].get("reason", ""), "a blocked task is not offered: the stop asks the agent to check it is still truly blocked"
    assert "blocked tasks: 1 the tree (waiting on: the payment sandbox coming back)" in console.run(["environment", "overview"], AGENT).text
    assert "open again" in console.run(["task", "unblock", "1"], AGENT).text and app.container.get(Tasks).find(1).state == TaskState.OPEN


def test_a_write_needs_no_task(app: App):
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    assert write(app)[0] == 200, "a quick edit is the agent's own; a task is for work worth tracking"

def test_the_menu_watcher_confirms_what_the_journal_caused_closes_what_it_cannot_place_and_leaves_the_users_own(app: App, monkeypatch):
    import os
    import time as timing
    from journal.engine.menu_watcher import MenuWatcher
    from journal.repositories.messages import Messages
    from journal.supervisor_link import SupervisorLink
    transmitted = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: transmitted.append({"verb": verb, **fields}))
    hook(app, "SessionStart")
    watcher, link = app.container.get(MenuWatcher), app.container.get(SupervisorLink)
    agent = app.container.get(SessionAgents).agent("s1", 1)
    screens = app.config.home / "runtime" / "screens"
    screens.mkdir(parents=True, exist_ok=True)
    (app.config.home / "runtime" / "inboxes").mkdir(parents=True, exist_ok=True)
    (app.config.home / "runtime" / "inboxes" / "main").write_text(json.dumps({"socket": "/tmp/none.sock", "protocol": 1, "screen": str(screens / "main.out")}))
    def shown(text: str, still_for: float = 5.0) -> None:
        path = screens / "main.out"
        path.write_text(text)
        os.utime(path, (timing.time() - still_for, timing.time() - still_for))
    switch = "\x1b[1mSwitch model?\x1b[0m\r\nYour next response will be slower\r\n\r\n❯ 1. Yes, switch to Opus 5.5\r\n  2. No, go back\r\n"
    link.choose(1, "/model opus")
    shown(switch)
    assert watcher.check(agent) == "\r" and transmitted[-1] == {"verb": "keys", "name": "agent", "keys": "\r"}, "a confirmation the journal's pick caused is taken with Enter"
    assert watcher.check(agent) == "", "and answered once"
    from journal.engine.support.menu_answers import MenuAnswers
    picks = {"Turn it on": 2, "Pick one": 0}
    monkeypatch.setattr(MenuAnswers, "ask", lambda self, menu, provider: self._asked.__setitem__(self.key(menu), next((o for o in menu.options if o.number == picks.get(menu.options[0].label)), None)))
    requested = app.container.get(MenuAnswers)
    resolved = lambda: [timing.sleep(0.05) for _ in range(40) if requested._running - set(requested._asked)]
    shown("Something new?\r\n❯ 1. Turn it on\r\n  2. Leave it alone for now\r\n")
    line_text = watcher.check(agent)
    resolved()
    assert (line_text or watcher.check(agent)) == "\x1b[B\r", "a menu the word rules cannot settle is answered by an independent agent asked off the watcher's thread"
    shown("Something else?\r\n❯ 1. Turn it on\r\n  2. Leave it alone for now\r\n")
    assert watcher.check(agent) == "\x1b[B\r", "and its pick is remembered for the same options"
    shown("Odd one?\r\n❯ 1. Pick one\r\n  2. Pick two\r\n")
    line_text = watcher.check(agent)
    resolved()
    assert (line_text or watcher.check(agent)) == "\x1b", "a menu even the asked agent cannot place is closed with Escape"
    from journal.repositories.scope import Scope
    with app.container.get(Scope).environment(1):
        assert any("closed it with Escape" in m.text for m in app.container.get(Messages).scoped()), "and a card says so"
    permission = "Bash command\r\nrm -f build/*.log\r\n\r\nDo you want to proceed?\r\n❯ 1. Yes\r\n  2. Yes, and don't ask again for rm commands in build\r\n  3. No, and tell Claude what to do differently (esc)\r\n"
    launches = app.config.home / "runtime" / "launches"
    launches.mkdir(parents=True, exist_ok=True)
    (launches / "main.json").write_text(json.dumps({"front": {"command": ["claude", "--settings", "{}"]}}))
    shown(permission)
    assert watcher.check(agent) != "\r", "a permission question under a launch that keeps the prompts is the user's to answer"
    (launches / "main.json").write_text(json.dumps({"front": {"command": ["claude", "--dangerously-skip-permissions", "--settings", "{}"]}}))
    shown(permission.replace("build", "dist"))
    assert watcher.check(agent) == "\r", "a permission question the provider asks anyway under a launch that skips the prompts is answered with yes"
    (screens / "main.keyed").touch()
    shown("Pick a theme\r\n❯ 1. Dark\r\n  2. Light\r\n")
    assert watcher.check(agent) == "", "a picker that came up right after keys at the keyboard is the user's own"
    shown(switch.replace("Opus 5.5", "Sonnet 5.5") + "\r\n──────\r\n❯ \r\n──────\r\n  agent-journal · main\r\n")
    assert watcher.check(agent) == "\r", "a yes-or-no confirmation of what the user just asked at the keyboard is confirmed, seen by its cursor though the prompt box is drawn below it"
    shown("Pick a colour\r\n❯ 1. Red\r\n  2. Blue\r\n", still_for=0.0)
    assert watcher.check(agent) == "", "a menu just drawn is not answered yet"
    busy = lambda seconds: f"· Shimmying… ({seconds}s · ↓ 3.9k tokens)\r\n\r\n────────────────\r\n" + switch.replace("Opus 5.5", "Fable 5.1")
    shown(busy(49), still_for=0.0)
    assert watcher.check(agent) == "", "a menu first seen under a moving spinner waits one look"
    shown(busy(51), still_for=0.0)
    assert watcher.check(agent) == "\r", "the switch of model is confirmed at the next look while the agent works, its spinner counting above the rule: the menu stood the same, whatever the screen did, and only a model change asks it"


def test_a_typed_line_goes_out_on_one_line(app: App, monkeypatch):
    """One with breaks would arrive as pasted text that never matches it, and be typed again."""
    from journal.supervisor_link import SupervisorLink
    transmitted = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: transmitted.append(fields))
    app.container.get(SupervisorLink).type(1, "the command finished: cat <<EOF\nx\nEOF")
    assert transmitted[-1]["line"] == "[journal] the command finished: cat <<EOF x EOF"


LINE = Nudge("tests", "line", "a line")
OTHER = Nudge("tests", "other", "another line")
WHY = Nudge("tests", "why", "held here")


class ServerCatalogue:
    def states(self):
        return [Ready, Working]

    def modes(self):
        return []

    def floors(self):
        return {}

    def silenced(self, nudge):
        return False


class Rows:
    def option(self, option):
        return {"tasks.log_after": 7}.get(option.key, option.default)


@dataclass(frozen=True)
class Listening(BaseState):
    name = "listening"

    def on_tool_starting(self, event: ToolStarting, settings: SettingsValue) -> Transition:
        return self.none(LINE)

    def on_agent_event(self, event: AgentEvent, settings: SettingsValue) -> Transition:
        return self.none(OTHER)

    def on_push(self, settings):
        return ()

    def label(self) -> str:
        return "not a listener"


def test_the_stack_keeps_its_bottom_changes_only_its_top_and_comes_back_from_its_data():
    stack = Stack((Ready(), Working(task_id=3)))
    assert stack.top() == Working(task_id=3)
    assert stack.pushed(Ended()).serialized()[-1] == {"state": "ended", "data": {}}
    assert stack.popped().serialized() == [{"state": "idle", "data": {"silenced_at": 0.0, "pause_reported": False, "stop_round": 0}}]
    assert stack.popped().popped() == stack.popped()
    assert stack.with_top(Working(task_id=4)).top().task_id == 4
    catalogue = StatesCatalogue(ServerCatalogue())
    assert catalogue.stack(Agent(stack=tuple(stack.serialized()))) == stack
    assert catalogue.stack(Agent(state="working", data={"task_id": 3})) == stack
    assert catalogue.stack(Agent(stack=({"state": "gone", "data": {}},))).top() == Ready()


def test_merged_answers_say_every_nudge_in_order_hold_on_the_first_and_move_once():
    idle = Ready()
    answers = [idle.none(LINE), idle.push(Working(task_id=1), OTHER), idle.refuse(WHY), idle.pop(), idle.refuse(OTHER)]
    merged = Transition.merged(idle, answers)
    assert merged.nudges == (LINE, OTHER)
    assert merged.pushed == Working(task_id=1) and not merged.popped
    assert merged.refusal is WHY
    assert merged.dropped == ("pop",)
    assert merged.target is idle
    assert Transition.merged(idle, [idle.swap(Working(task_id=2))]).target == Working(task_id=2)
    assert Transition.merged(idle, []).target is idle


def test_every_listener_whose_event_matches_runs_the_most_specific_first_and_the_engine_conduct_hears_compaction_and_the_end():
    from journal.engine.safety_conduct import SafetyConduct
    settings, state, safety = SettingsValue({}), Listening(), (SafetyConduct,)
    assert state.respond(ToolStarting(call=ToolCall(tool="Write", input={}, operation=Claude().operation("Write", {}))), settings).nudges == (LINE, OTHER)
    assert state.respond(SessionEnded(), settings).nudges == (OTHER,)
    assert state.respond(Event(), settings) == state.none()
    assert state.respond(Compacting(), settings, safety).pushed == CompactingState()
    assert state.respond(SessionEnded(), settings, safety).pushed == Ended()
    assert Ended().respond(SessionEnded(), settings, safety).pushed is None, "a session already over is not ended again"
    assert [method.__name__ for _, method in Listening.listeners()] == ["on_tool_starting", "on_agent_event"]
    assert [method.__name__ for _, method in Listening.listeners(safety)][-4:] == ["on_compacting", "on_session_ended", "on_session_retired", "on_stop"]


def test_settings_is_a_frozen_value_of_the_options_read_by_option():
    option = Option("tasks.log_after", "Log after", "", 50)
    assert SettingsValue.applied(Rows(), [option]).value(option) == 7


def test_every_shipped_option_is_declared_with_the_kind_of_its_default(app: App):
    kinds = {"number": (int, float), "switch": (bool,), "text": (str,), "choice": (str,), "lines": (list, tuple)}
    wrong = [option.key for option in app.container.get(Registry).options() if option.kind in kinds and (not isinstance(option.default, kinds[option.kind]) or option.kind == "number" and isinstance(option.default, bool))]
    assert not wrong, f"declared with a kind their default is not, so journal settings set refuses a right value: {wrong}"


def test_every_agent_event_carries_the_time_it_was_placed_and_a_tick_carries_its_own():
    placed = ToolStarting(call=ToolCall(tool="Write", input={}, operation=Claude().operation("Write", {}))).placed("s1", 1, "claude", None, 12.5)
    assert placed.time == 12.5 and placed.session == "s1"
    assert Ticked(session="s1", environment_id=1, time=3.0, silence_seconds=0.0).time == 3.0


def test_a_renamed_state_answers_as_before_through_its_on_listeners_and_a_plain_method_is_none():
    settings = SettingsValue({})
    assert Ended().respond(ToolStarting(call=ToolCall(tool="Write", input={}, operation=Claude().operation("Write", {}))), settings).popped
    assert Ended().respond(SessionEnded(), settings) == Ended().none()
    names = [method.__name__ for _, method in Ended.listeners()]
    assert set(names) == {"on_session_started", "on_prompt_submitted", "on_tool_starting"}


def test_the_stack_is_seeded_from_the_state_and_its_pause_chain_unwound_with_idle_at_the_bottom(connection, bus, scope):
    agents = Agents(connection, bus, scope, TimeSource())
    stuck = agents.save(Agent(environment_id=1, session="s9", state="stuck", data={"resume": {"state": "working", "data": {"task_id": 3, "resume": {"state": "idle", "data": {}}}}}), Actor.system())
    missing = agents.save(Agent(environment_id=1, session="s8", state="gone", data={}), Actor.system())
    StackSeed().apply(connection)
    assert agents.find(stuck.id).stack == ({"state": "idle", "data": {}}, {"state": "working", "data": {"task_id": 3}}, {"state": "stuck", "data": {}})
    assert agents.find(missing.id).stack == ({"state": "idle", "data": {}}, {"state": "gone", "data": {}})


def test_the_session_end_pushes_ended_on_the_stack_and_a_new_start_pops_it(app: App):
    hook(app, "SessionStart")
    hook(app, "SessionEnd")
    agents = app.container.get(Agents)
    assert [row["state"] for row in agents.session_agent("s1").stack] == ["idle", "ended"]
    hook(app, "SessionStart")
    assert [row["state"] for row in agents.session_agent("s1").stack] == ["idle"]


CALLS: list[str] = []


@dataclass(frozen=True)
class Noting(Wait):
    name = "noting"

    def on_push(self, settings):
        CALLS.append("push noting")
        return (LINE.create(),)

    def on_pop(self, settings):
        CALLS.append("pop noting")
        return ()


@dataclass(frozen=True)
class Refusing(Wait):
    name = "refusing"

    def on_push(self, settings):
        return Block(WHY.create())


@dataclass(frozen=True)
class Catching(BaseState):
    name = "catching"

    def on_pause(self, settings):
        CALLS.append("pause catching")
        return ()

    def on_resume(self, data: FeatureData, settings):
        CALLS.append("resume catching")
        return self.pop()


def test_the_lifecycle_hooks_run_in_order_say_their_lines_refuse_a_push_and_catch_up_beneath_a_pop(app: App):
    CALLS.clear()
    hook(app, "SessionStart")
    machine, settings = app.container.get(StateMachine), SettingsValue({WorkersOptions.MODE.key: "builder"})
    data = Stack((Ready(), Catching()))
    pushed = machine.hook_machine(data, data.pushed(Noting()), settings, FeatureData({}))
    assert pushed.stack == data.pushed(Noting()) and pushed.nudges == (LINE.create(),) and pushed.refusal is None
    refused = machine.hook_machine(data, data.pushed(Refusing()), settings, FeatureData({}))
    assert refused.stack == data and refused.refusal == Block(WHY.create())
    popped = machine.hook_machine(data.pushed(Noting()), data, settings, FeatureData({}))
    assert popped.stack == Stack((Ready(),)) and popped.nudges == ()
    assert CALLS == ["pause catching", "push noting", "pause catching", "pop noting", "resume catching"]
    with pytest.raises(Rejection):
        machine.push("s1", 1, Refusing(), Actor.system(), "a refused push")
    assert [row["state"] for row in app.container.get(Agents).session_agent("s1").stack] == ["idle"]


def test_a_push_and_a_pop_write_the_trail_and_the_agents_page_shows_the_stack_top_first(app: App):
    hook(app, "SessionStart")
    app.console().run(["task", "create", "t", "--start"], AGENT)
    app.console().run(["stuck", "lost"], AGENT)
    with app.container.get(Scope).environment(1):
        row = next(item for item in app.container.get(AgentActivity).page(app.container.get(Agents).scoped()) if item["session"] == "s1")
    assert [s["name"] for s in row["stack"]] == ["stuck", "working", "idle"] and row["stack"][0]["awaits"]
    assert [(t["before"], t["after"]) for t in row["trail"]] == [([], ["idle"]), (["idle"], ["idle", "working"]), (["idle", "working"], ["idle", "working", "stuck"])]
    write(app)
    with app.container.get(Scope).environment(1):
        trail = [e.data for e in app.container.get(Entries).kind_entries(StackHistory.KIND) if e.data["session"] == "s1"]
    popped = next(e for e in trail if [row["state"] for row in e["before"]] == ["idle", "working", "stuck"])
    assert popped["after"][-1]["state"] == "working" and popped["cause"]
    before = app.container.get(Agents).session_agent("s1").data
    for _ in range(3):
        hook(app, "PreToolUse", tool_name="Read", tool_input={"file_path": "a.py"})
    with app.container.get(Scope).environment(1):
        moves = [e.data for e in app.container.get(Entries).kind_entries(StackHistory.KIND) if e.data["session"] == "s1"]
    assert app.container.get(Agents).session_agent("s1").data != before and len(moves) == len(trail), "a state whose counts change in place moves nothing, so the trail keeps only pushes and pops"


def test_a_worker_has_a_stack_of_its_own_from_clock_in_to_clock_out_and_none_of_the_main_agents_conduct(app: App):
    from journal.models.author import Author
    from journal.models.message import Message
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.messages import Messages
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.support.agent_token import AgentToken
    hook(app, "SessionStart")
    scope, workers, tasks, agents = app.container.get(Scope), app.container.get(Workers), app.container.get(Tasks), app.container.get(Agents)
    with scope.environment(1):
        worker = workers.save(Worker(environment_id=1, name="Mr. Babbage", brief="b", session="w1", token_hash=AgentToken.hashed("tok")), Actor.system())
        task = tasks.save(Task(environment_id=1, title="the parser", brief="the parser reads"), Actor.system())
        tasks.handover(task, Ref.build(worker), Actor.system())
    def worker_hook(kind: str, **body):
        data = json.dumps({"hook_event_name": kind, "session_id": "w1", **body}).encode()
        request = HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=data, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main", "X-Journal-Actor": f"worker:{worker.id}", "X-Journal-Actor-Token": "tok"})
        try:
            with urlopen(request, timeout=5) as reply:
                return reply.status, json.loads(reply.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())
    app.console().run(["panic", "paused"], AGENT)
    posted = lambda: len([m for m in app.container.get(Messages).all() if m.data.get("shows") != "workers"])
    with scope.environment(1):
        messages = posted()
    assert write(app)[0] == 409, "the main agent's pause holds its own write"
    assert worker_hook("SessionStart", source="startup") == (200, {}), "a worker owes no overview"
    status, body = worker_hook("PreToolUse", tool_name="Write", tool_input={"file_path": "a.py"})
    assert status == 409 and "you are not at work" in body["error"] and "paused" not in body["error"], "before it clocks in a worker rests on Void, which holds every tool but a journal command with its own line alone"
    assert worker_hook("PreToolUse", tool_name="Bash", tool_input={"command": "journal clock-in"})[0] == 200, "the clock-in call itself passes"
    with scope.environment(1):
        workers.save(workers.find(worker.id).ready(1.0), Actor.worker(worker.id))
    assert agents.session_agent("w1").stack[-1]["state"] == "working_task" and app.container.get(SessionAgents).top("w1").task_id == task.id, "clocking in puts it to work on the task it holds"
    with scope.environment(1):
        app.container.get(Messages).save(Message(environment_id=1, author=Author.USER, text="for the main agent"), Actor.user(1))
        messages = posted()
    writes = [worker_hook("PreToolUse", tool_name="Write", tool_input={"file_path": f"w{n}.py"}) for n in range(8)]
    assert all(status == 200 for status, _ in writes), "a worker is never held by the user's unread messages, which are the main agent's to read"
    with scope.environment(1):
        workers.save(workers.find(worker.id).with_(edit_lock=True), Actor.system())
    status, body = worker_hook("PreToolUse", tool_name="Write", tool_input={"file_path": "locked.py"})
    assert status == 409 and "the journal is rebasing your worktree" in body["error"], "a worker's writes wait while the journal rebases its worktree"
    with scope.environment(1):
        workers.save(workers.find(worker.id).with_(edit_lock=False), Actor.system())
    for line in ("git commit -qm work", "git -C platform status", "cd platform && git rebase main"):
        status, body = worker_hook("PreToolUse", tool_name="Bash", tool_input={"command": line})
        assert status == 409 and "you never run git: the journal commits your work" in body["error"], (line, body)
    with scope.environment(1):
        workers.save(workers.find(worker.id).delivered(2.0), Actor.worker(worker.id))
    assert agents.session_agent("w1").stack[-1]["state"] == "void" and "decision" not in worker_hook("Stop")[1], "clocked out, it falls back to Void and may stop"
    with scope.environment(1):
        assert posted() == messages, "none of its hooks is posted in the chat, only its marks"
        assert {"SessionStart", "PreToolUse", "Stop"} <= {entry.data["hook_event_name"] for entry in app.container.get(Entries).all() if entry.data.get("session_id") == "w1"}, "its hooks are recorded"
    app.console().run(["panic", "pop"], AGENT)
    stack = agents.session_agent("w1").stack
    app.container.get(Bus).dispatch(PlanStarted(environment_id=1, time=1.0, plan_id=1, task_id=0))
    assert agents.session_agent("w1").stack == stack and agents.session_agent("s1").stack[-1]["state"] == "following_plan", "a row event for the environment reaches the main agent alone"


def test_a_worker_clocking_out_leaves_another_workers_stack_alone(app: App):
    from journal.support.agent_role import AgentRole
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.support.agent_token import AgentToken
    hook(app, "SessionStart")
    scope, workers, tasks, agents = app.container.get(Scope), app.container.get(Workers), app.container.get(Tasks), app.container.get(Agents)
    with scope.environment(1):
        first = workers.save(Worker(environment_id=1, name="Mr. A", brief="a", session="wa", token_hash=AgentToken.hashed("ta")), Actor.system())
        second = workers.save(Worker(environment_id=1, name="Mr. B", brief="b", session="wb", token_hash=AgentToken.hashed("tb")), Actor.system())
        for worker, title in ((first, "the parser"), (second, "the lexer")):
            tasks.handover(tasks.save(Task(environment_id=1, title=title, brief=f"{title} reads"), Actor.system()), Ref.build(worker), Actor.system())
            agents.save(Agent(environment_id=1, session=worker.session, provider="claude", state="void", role=AgentRole.WORKER), Actor.system())
    with scope.environment(1):
        workers.save(workers.find(first.id).ready(1.0), Actor.worker(first.id))
        workers.save(workers.find(second.id).ready(1.0), Actor.worker(second.id))
    assert agents.session_agent("wa").stack[-1]["state"] == agents.session_agent("wb").stack[-1]["state"] == "working_task", "each worker clocked in works on its own task"
    second_stack = agents.session_agent("wb").stack
    with scope.environment(1):
        workers.save(workers.find(first.id).delivered(2.0), Actor.worker(first.id))
    assert agents.session_agent("wa").stack[-1]["state"] == "void", "the worker that clocked out leaves its work"
    assert agents.session_agent("wb").stack == second_stack, "the other worker's stack is left as it was"


def test_a_worker_clocks_in_on_its_task_and_the_main_agent_is_not_told_back_what_it_dispatched(app: App, monkeypatch):
    from journal.models.support.ref import Ref
    from journal.models.agent import Agent
    from journal.support.agent_role import AgentRole
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.supervisor_link import SupervisorLink
    typed = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: typed.append(fields.get("line", "")))
    hook(app, "SessionStart")
    scope, workers, tasks, agents = app.container.get(Scope), app.container.get(Workers), app.container.get(Tasks), app.container.get(Agents)
    with scope.environment(1):
        worker = workers.save(Worker(environment_id=1, name="Mr. Babbage", brief="b", session="w1", dispatcher="s1"), Actor.system())
        task = tasks.save(Task(environment_id=1, title="the parser", brief="the parser reads"), Actor.system())
        tasks.handover(task, Ref.build(worker), Actor.system())
        agents.save(Agent(environment_id=1, session="w1", provider="claude", state="void", role=AgentRole.WORKER), Actor.system())
    babbage = Caller.worker("main", worker.id, "w1", "claude")
    assert app.console().run(["clock-in"], babbage).code == 0
    assert app.container.get(SessionAgents).top("w1").task_id == task.id, "clocking in moves the worker to Working on its task"
    with scope.environment(1):
        assert tasks.find(task.id).delegated, "and keeps the task delegated to it"
    assert not any("clocked in" in line for line in typed), "the main agent dispatched the worker, so it is not told the worker is at work"
    assert "a worker clocks in once each time it is sent" in app.console().run(["clock-in"], babbage).error
    with scope.environment(1):
        workers.save(workers.find(worker.id).with_(state=WorkerState.DISPATCHED), Actor.system())
    assert app.console().run(["clock-in"], babbage).code == 0 and app.container.get(SessionAgents).top("w1").task_id == task.id, "a worker sent back clocks in again"


def test_a_worker_sent_back_ended_or_stopped_is_told_to_its_dispatcher_in_one_short_line():
    from journal.features.workers.workers_conduct import WorkersConduct
    from pathlib import Path
    from journal.events.feature_data import FeatureData
    from journal.features.workers.support.workers_data import WorkersData
    from journal.events.rows.proof_short import ProofShort
    from journal.events.rows.worker_mention import WorkerMention
    from journal.events.rows.worker_stopped import WorkerStopped
    from journal.events.rows.worker_unfinished import WorkerUnfinished
    settings = SettingsValue({WorkersOptions.MODE.key: "builder"})
    workers = lambda *resumable: FeatureData({"workers": WorkersData(dispatched_workers=(), idle_workers=(), active_subagents=0, subagents=(), worktrees_root=Path("."), worktrees=(), resumable=resumable)})
    said = lambda event, *resumable: [n.rendered() for n in Ready().respond(event.with_data(workers(*resumable)), settings, (WorkersConduct,)).nudges]
    short = ProofShort(environment_id=1, time=1.0, task_id=5, worker_id=3, point=2, shortfall="the tests", dispatcher="s1")
    assert said(short.reaching("s1")) == ["worker 3 back on point 2"], "a worker sent back is told as one line with ids"
    assert said(short.reaching("s2")) == [], "to the agent that dispatched it alone"
    second = replace(short, prior_shortfalls=("the alias names are missing",))
    assert said(second.reaching("s1")) == ["worker 3 back on point 2 again; earlier: the alias names are missing"], "the second send-back of a task says so, with the first reason"
    third = replace(short, prior_shortfalls=("the alias names are missing", "the tests do not run"), model="sonnet")
    assert said(third.reaching("s1")) == ['worker 3 back on point 2 3 times on sonnet; earlier: the alias names are missing; the tests do not run. change the target or the worker, or send its next job on a stronger model: journal worker send 3 --model <model> "<job>"'], "the third names the model and tells the orchestrator to change the target, the worker or the model"
    fourth = replace(short, prior_shortfalls=("the alias names are missing", "the tests do not run", "the lexer"), model="sonnet")
    assert said(fourth.reaching("s1")) == ["worker 3 back on point 2 again; earlier: the alias names are missing; the tests do not run; the lexer"], "the change is told once: a fourth is told as a send-back again"
    worker = WorkerMention(3, "Lady Lovelace", "s1")
    ended = lambda times, limit=False: WorkerUnfinished(environment_id=1, time=1.0, worker=worker, ref="workers:3", outcome="worker 3, ended", times=times, is_run_limit=limit).reaching("s1")
    assert said(ended(1), 3) == [], "a run that ends without clocking out is not told the first time: the journal asks the worker itself"
    assert said(ended(2), 3) == ["worker 3 ended without clocking out"], "but the second time"
    assert said(ended(1)) == ["worker 3 ended without clocking out"], "or at once when there is no session or conversation to ask in"
    assert said(ended(2, True), 3) == ["worker 3 ended without clocking out: run limit"], "and it says when the run limit was the cause"
    stopped = lambda limit: WorkerStopped(environment_id=1, time=1.0, worker=worker, ref="workers:3", outcome="worker 3, stopped", is_run_limit=limit).reaching("s1")
    assert said(stopped(False)) == ["worker 3 stopped before it reported"] and said(stopped(True)) == ["worker 3 stopped before it reported: run limit"]


def test_a_run_that_ended_without_clocking_out_is_asked_by_the_journal_itself_to_clock_out_once():
    from journal.events.rows.worker_mention import WorkerMention
    from journal.events.rows.worker_unfinished import WorkerUnfinished
    from journal.features.workers.listeners.unfinished_clock_out import CLOCK_OUT_REQUEST, UnfinishedClockOut

    class Actions:
        def __init__(self) -> None:
            self.sent = []

        def send(self, n, brief, dispatcher, actor):
            self.sent.append((n, brief, actor))

    class Workers:
        def find(self, n):
            return n

    class Resumes:
        def is_resumable(self, worker):
            return worker == 3

    actions = Actions()
    ask = UnfinishedClockOut(actions, Workers(), Resumes())
    ended = lambda times, n=3: WorkerUnfinished(environment_id=1, time=1.0, worker=WorkerMention(n, "Lady Lovelace", "s1"), ref=f"workers:{n}", outcome="o", times=times)
    ask.handle(ended(1))
    ask.handle(ended(2))
    ask.handle(ended(1, 4))
    assert actions.sent == [(3, CLOCK_OUT_REQUEST, Actor.system())] and "journal clock-out" in CLOCK_OUT_REQUEST, "the journal asks the worker to clock out, in its own words, the first time only, and only a worker that can go on in its session"


def test_a_worker_keeps_its_own_to_do_list_inside_its_task(app: App):
    from journal.http.controllers.tasks import TaskController
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.support.agent_token import AgentToken
    hook(app, "SessionStart")
    scope, tasks = app.container.get(Scope), app.container.get(Tasks)
    with scope.environment(1):
        worker = app.container.get(Workers).save(Worker(environment_id=1, name="Mr. Babbage", brief="b", session="w1", token_hash=AgentToken.hashed("tok")), Actor.system())
        task = tasks.save(Task(environment_id=1, title="the parser", brief="the parser reads"), Actor.system())
        tasks.handover(task, Ref.build(worker), Actor.system())
    babbage, console = Caller.worker("main", worker.id, "w1", "claude"), app.console()
    assert console.run(["clock-in"], babbage).code == 0, "the worker clocks in on its task, so its stop is its working state's"
    for item in ("write the grammar", "write the test", "run it"):
        assert console.run(["todo", "add", item], babbage).code == 0
    assert console.run(["todo", "check", "2"], babbage).code == 0 and "has 3 items" in console.run(["todo", "check", "7"], babbage).error
    assert console.run(["todo", "list"], babbage).text.splitlines() == ["  1  [ ]  write the grammar", "  2  [x]  write the test", "  3  [ ]  run it"], "the items read back in order, one complete"
    assert "only a worker on a task keeps one" in console.run(["todo", "list"], AGENT).error
    with scope.environment(1):
        shown = app.container.get(TaskController).shown_page([tasks.find(task.id)])[0]
    assert [(item.text, item.complete) for item in shown["work"].todos] == [("write the grammar", False), ("write the test", True), ("run it", False)], "the task's payload carries the items with their flags"
    data = json.dumps({"hook_event_name": "Stop", "session_id": "w1"}).encode()
    request = HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=data, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main", "X-Journal-Actor": f"worker:{worker.id}", "X-Journal-Actor-Token": "tok"})
    with urlopen(request, timeout=5) as reply:
        answered = reply.read().decode()
    assert "2 open items: 1. write the grammar; 3. run it" in answered, "the worker's stop is told the items still open"


def test_a_workers_stop_is_held_while_its_own_output_runs_and_told_its_end(app: App):
    from journal.engine.command_events import CommandEvents
    from journal.models.command_output import CommandOutput
    from journal.models.worker import Worker
    from journal.repositories.command_outputs import CommandOutputs
    from journal.repositories.workers import Workers
    from journal.support.agent_token import AgentToken
    hook(app, "SessionStart")
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.repositories.tasks import Tasks
    scope = app.container.get(Scope)
    with scope.environment(1):
        worker = app.container.get(Workers).save(Worker(environment_id=1, name="Mr. Babbage", brief="b", session="w1", token_hash=AgentToken.hashed("tok")), Actor.system())
        tasks = app.container.get(Tasks)
        tasks.handover(tasks.save(Task(environment_id=1, title="the parser", brief="the parser reads"), Actor.system()), Ref.build(worker), Actor.system())
        app.container.get(Workers).save(app.container.get(Workers).find(worker.id).ready(1.0), Actor.worker(worker.id))
    def worker_stop() -> dict:
        data = json.dumps({"hook_event_name": "Stop", "session_id": "w1"}).encode()
        request = HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=data, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main", "X-Journal-Actor": f"worker:{worker.id}", "X-Journal-Actor-Token": "tok"})
        with urlopen(request, timeout=5) as reply:
            return json.loads(reply.read())
    assert "decision" not in worker_stop(), "a worker with nothing running may stop"
    with scope.environment(1):
        outputs = app.container.get(CommandOutputs)
        output = outputs.save(CommandOutput(environment_id=1, command="pytest -q", session="w1", moved=True), Actor.worker(worker.id))
    held = worker_stop()
    assert held["decision"] == "block" and f"your output {output.id} still runs" in held["reason"], "its stop is held while its own background output runs"
    with scope.environment(1):
        ended = outputs.save(output.with_(ended=True, status=0), Actor.system())
        app.container.get(CommandEvents).ended(ended, app.container.get(Agents).session_agent("w1"))
    told = worker_stop()
    assert told["decision"] == "block" and f"output {output.id} ended with code 0" in told["reason"], "the output's end comes back in the answer to its next stop"
    assert "decision" not in worker_stop(), "told once"


def test_the_users_edits_and_closes_of_a_workers_task_reach_the_worker(app: App):
    from datetime import datetime, timezone
    from journal.http.controllers.tasks import TaskController
    from journal.models.agent import Agent
    from journal.support.agent_role import AgentRole
    from journal.models.proof import Proof
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.repositories.proofs import Proofs
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    hook(app, "SessionStart")
    scope, workers, tasks, agents, proofs = app.container.get(Scope), app.container.get(Workers), app.container.get(Tasks), app.container.get(Agents), app.container.get(Proofs)
    def worker_on(title: str, session: str) -> tuple:
        with scope.environment(1):
            worker = workers.save(Worker(environment_id=1, name=f"worker on {title}", brief="b", session=session), Actor.system())
            task = tasks.save(Task(environment_id=1, title=title, brief="- reads the grammar\n- names each rule"), Actor.system())
            tasks.handover(task, Ref.build(worker), Actor.system())
            agents.save(Agent(environment_id=1, session=session, provider="claude", state="void", role=AgentRole.WORKER), Actor.system())
        app.console().run(["clock-in"], Caller.worker("main", worker.id, session, "claude"))
        return worker, task
    worker, task = worker_on("the parser", "w1")
    with scope.environment(1):
        for point in (1, 2):
            proofs.added(Proof(environment_id=1, point=point, text="shown"), task, Actor.worker(worker.id))
    assert app.console().run(["task", "brief", str(task.id), "- reads the grammar\n- names each rule and its alias"], USER).code == 0
    app.runtime().deferred.drain()
    with scope.environment(1):
        assert [(p.point, p.state) for p in proofs.task_proofs(tasks.find(task.id))] == [(1, "shown"), (2, "stale")], "a rewritten point's proof goes stale"
        assert f"task {task.id} changed: point 2 of its brief rewritten" in " ".join(agents.session_agent("w1").queued_lines), "and the worker is told which points changed"
    controller = app.container.get(TaskController)
    with scope.environment(1):
        tasks.save(tasks.find(task.id).cancelled(datetime.now(timezone.utc), "no longer wanted"), Actor.user(1))
    app.runtime().deferred.drain()
    assert app.container.get(SessionAgents).top("w1").name != "working" and "the user closed your task" in " ".join(agents.session_agent("w1").queued_lines), "the user's cancel ends the worker's work, and it is told"
    with scope.environment(1):
        assert workers.find(worker.id).state == WorkerState.RELEASED and tasks.holder(tasks.find(task.id)) is None, "and releases it"
    second, held = worker_on("the lexer", "w2")
    request = type("Posted", (), {"number": lambda self, key: held.id, "environment": "main", "actor": Actor.user(1), "body": {}})()
    with scope.environment(1):
        controller.start(request)
        assert tasks.holder(tasks.find(held.id)) == Ref.build(second), "the viewer's start of a held task leaves its holder"
        controller.finish(type("Posted", (), {"number": lambda self, key: held.id, "environment": "main", "actor": Actor.user(1), "body": {"how": "written by hand"}})())
    app.runtime().deferred.drain()
    with scope.environment(1):
        assert workers.find(second.id).state == WorkerState.RELEASED, "the user's finish releases the worker"


def test_journal_panic_passes_every_hold_and_a_compaction_ends_at_the_journals_start(app: App):
    hook(app, "SessionStart")
    console, agents = app.console(), app.container.get(Agents)
    console.run(["panic", "paused"], AGENT)
    assert write(app)[0] == 409, "the pause holds every tool"
    assert hook(app, "PreToolUse", tool_name="Bash", tool_input={"command": "journal panic apply idle"})[0] == 200, "a panic line passes the hold"
    assert hook(app, "PreToolUse", tool_name="Bash", tool_input={"command": "journal panic apply idle && rm -rf a"})[0] == 409, "only a line of panic alone passes"
    console.run(["panic", "pop"], AGENT)
    hook(app, "PreCompact")
    assert agents.session_agent("s1").state == "compacting"
    app.container.get(StateMachine).compactions_ended()
    assert [row["state"] for row in agents.session_agent("s1").stack] == ["idle"], "a journal start ends every compaction"


def test_journal_panic_pushes_pops_and_empties_the_stack_by_hand_and_the_trail_names_the_agent(app: App):
    hook(app, "SessionStart")
    console, agents = app.console(), app.container.get(Agents)
    assert console.run(["panic", "working", "focus=parsing"], AGENT).text.strip() == "the stack, bottom to top: idle, working(focus=parsing)"
    assert console.run(["panic", "stuck", "reason=lost"], AGENT).text.startswith("the stack, bottom to top: idle, working(focus=parsing), stuck(")
    assert console.run(["panic", "pop"], AGENT).text.strip().endswith("idle, working(focus=parsing)")
    assert console.run(["panic", "nowhere"], AGENT).code != 0
    assert console.run(["panic", "idle"], AGENT).text.strip() == "the stack, bottom to top: idle"
    assert [row["state"] for row in agents.session_agent("s1").stack] == ["idle"]
    with app.container.get(Scope).environment(1):
        newest = app.container.get(Entries).kind_entries(StackHistory.KIND)[0]
    assert newest.data["cause"] == "journal panic idle" and newest.actor == AGENT.actor


class Hearing(Listener[PlanStarted]):
    def __init__(self) -> None:
        self.heard: list[PlanStarted] = []

    def handle(self, event: PlanStarted) -> None:
        self.heard.append(event)


def test_a_saved_started_plan_sends_plan_started_once_and_a_plain_edit_sends_none(app: App):
    hearing = Hearing()
    app.container.get(Bus).listen(PlanStarted, hearing)
    plans, tasks = app.container.get(Plans), app.container.get(Tasks)
    with app.container.get(Scope).environment(1):
        task = tasks.save(Task(environment_id=1, title="first"), Actor.system())
        plan = plans.save(Plan(environment_id=1, title="p", state=PlanState.APPROVED), Actor.system())
        started = plans.save(plan.started(task, 5.0), Actor.system())
        assert started.events == () and hearing.heard == [PlanStarted(environment_id=1, time=5.0, row_id=plan.id, actor="system", plan_id=plan.id, task_id=task.id)]
        plans.save(started.with_(title="renamed"), Actor.system())
        assert len(hearing.heard) == 1


def test_a_plans_phase_in_hand_checkpoint_and_next_task_come_from_counts_and_one_link_a_phase_never_its_tasks_rows(app: App):
    from journal.db.connection import Connection
    from journal.models.link import Link
    from journal.models.phase import Phase
    from journal.models.support.ref import Ref
    from journal.repositories.links import Links
    from journal.repositories.load_tally import LoadTally
    from journal.repositories.phases import Phases
    from journal.repositories.plans import PHASE_LINK, PHASE_TASK_LINK
    from journal.repositories.tasks import PLAN_LINK
    plans, tasks, links, phases, actor = app.container.get(Plans), app.container.get(Tasks), app.container.get(Links), app.container.get(Phases), Actor.system()
    with app.container.get(Scope).environment(1):
        plan = plans.save(Plan(environment_id=1, title="p", state=PlanState.APPROVED), actor)
        first, second = [phases.save(Phase(environment_id=1, title=title, checkpoint=title == "one"), actor) for title in ("one", "two")]
        for phase in (first, second):
            links.save(Link(source=Ref.build(phase), target=Ref.build(plan), kind=PHASE_TASK_LINK), actor)
        rows = [tasks.save(Task(environment_id=1, title=title), actor) for title in ("a", "b", "c", "loose")]
        for task in rows:
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), kind=PLAN_LINK), actor)
        for task, phase in ((rows[1], first), (rows[0], first), (rows[2], second)):
            links.save(Link(source=Ref.build(task), target=Ref.build(phase), kind=PHASE_LINK), actor)
        assert [phase.id for phase in plans.plan_phases(plan)] == [first.id, second.id], "in the order they were added"
        LoadTally.begin()
        states = plans.phase_states(plan)
        assert "tasks" not in {count.model for count in LoadTally.ended().counts}, "no task row is read"
        assert plans.phase_task_ids([first, second]) == {first.id: [rows[1].id, rows[0].id], second.id: [rows[2].id]}, "each phase's tasks in the order they joined it"
        assert plan.current_phase(states) == 1 and plan.checkpoint_phase(states) is None
        app.container.get(Connection).cache.cleared()
        LoadTally.begin()
        assert plans.next_task(plan).id == rows[1].id, "the first open task of the first phase, in the order it joined the phase"
        assert [count.rows for count in LoadTally.ended().counts if count.model == "tasks"] == [1], "only the task found is read"
        for task in rows[:2]:
            tasks.save(task.completed(datetime.now(timezone.utc), "done"), actor)
        states = plans.phase_states(plan)
        assert plan.current_phase(states) == 2 and plan.checkpoint_phase(states).number == 1, "phase one done and phase two not begun: the checkpoint"
        assert plans.next_task(plan).id == rows[2].id and plans.remaining_count(plan) == 2 and not plans.is_stalled(plan)
        tasks.save(tasks.find(rows[2].id).started(datetime.now(timezone.utc)).paused("later", datetime.now(timezone.utc)), actor)
        assert plans.resumable(plan).id == rows[2].id and plans.next_task(plan).id == rows[3].id, "a paused task is resumed before the open one under no phase"
        tasks.save(tasks.find(rows[2].id).started(datetime.now(timezone.utc)), actor)
        assert plans.checkpoint_plans(plan) is None and plans.started_task(plan).id == rows[2].id, "phase two begun"


def test_a_hub_task_and_a_hub_plan_bound_to_an_environment_read_as_its_work_and_their_events_reach_its_agent_with_no_local_row(app: App):
    from journal.models.environment import Environment
    from journal.models.link import Link
    from journal.models.phase import Phase
    from journal.models.support.ref import Ref
    from journal.repositories.environments import Environments
    from journal.repositories.links import Links
    from journal.repositories.phases import PHASE_TASK_LINK, Phases
    from journal.repositories.scope import BOUND_LINK
    from journal.repositories.tasks import PLAN_LINK

    heard: list[TaskStarted] = []

    class StartedTasks(Listener[TaskStarted]):
        def handle(self, event: TaskStarted) -> None:
            heard.append(event)

    assert hook(app, "SessionStart")[0] == 200
    environments, plans, tasks, phases, links, scope = (app.container.get(kind) for kind in (Environments, Plans, Tasks, Phases, Links, Scope))
    actor = Actor.system()
    main = environments.existing("main")
    hub = environments.save(Environment.hub("k-acme", "acme"), actor)
    with scope.environment(hub.row_id):
        task = tasks.save(Task(environment_id=hub.row_id, title="the team's task"), actor)
        plan = plans.save(Plan(environment_id=hub.row_id, title="the team's plan", state=PlanState.APPROVED), actor)
        phase = phases.save(Phase(environment_id=hub.row_id, title="one"), actor)
        planned = tasks.save(Task(environment_id=hub.row_id, title="in the team's plan"), actor)
    links.save(Link(source=Ref.build(phase), target=Ref.build(plan), kind=PHASE_TASK_LINK), actor)
    links.save(Link(source=Ref.build(planned), target=Ref.build(plan), kind=PLAN_LINK), actor)
    local_rows = (len(tasks.global_matching(environment_id=main.row_id)), len(plans.global_matching(environment_id=main.row_id)), len(phases.global_matching(environment_id=main.row_id)))
    with scope.environment(main.row_id):
        assert not {task.id, planned.id} & {row.id for row in tasks.scoped()} and plan.id not in {row.id for row in plans.scoped()}, "a hub row is no environment's work until it is bound"
    for row in (task, plan):
        links.save(Link(source=Ref.build(row), target=Ref(Environment.table(), main.row_id), kind=BOUND_LINK), actor)
    with scope.environment(main.row_id):
        assert {task.id, planned.id} <= {row.id for row in tasks.open_tasks()} and plan.id in {row.id for row in plans.scoped()}, "the bound task and plan read as the environment's work"
        assert [row.id for row in plans.plan_phases(plan)] == [phase.id] and plans.remaining_count(plan) == 1 and plans.next_task(plan).id == planned.id, "and the bound plan's phases and tasks with it"
    app.container.get(Bus).listen(TaskStarted, StartedTasks())
    with scope.environment(main.row_id):
        for row in (task, planned):
            tasks.save(tasks.find(row.id).started(datetime.now(timezone.utc)), actor)
    assert [(event.environment_id, event.bound_environment_ids) for event in heard] == [(hub.row_id, (main.row_id,))] * 2, "each event is the hub's, bound to the environment, the plan's task through its plan"
    machine = app.container.get(StateMachine)
    assert all("s1" in {agent.session for agent in machine.audience(event)} for event in heard), "and reaches the environment's agent"
    assert {tasks.find(row.id).environment_id for row in (task, planned)} == {hub.row_id}, "the rows stay the hub's"
    assert (len(tasks.global_matching(environment_id=main.row_id)), len(plans.global_matching(environment_id=main.row_id)), len(phases.global_matching(environment_id=main.row_id))) == local_rows, "and no local task, plan or phase is made"


def test_the_models_carry_the_events_their_changes_mean():
    time = datetime(2026, 10, 20, 23, 0, tzinfo=timezone.utc)
    task = Task(id=7, environment_id=1, title="t", state=TaskState.STARTED)
    assert [type(e) for e in task.completed(time, "x").events] == [TaskClosed, RowResolved] and task.completed(time, "x").events[1].ref == "tasks:7"
    assert task.paused("later", time).events[0] == TaskClosed(environment_id=1, time=time.timestamp(), task_id=7, outcome="paused")
    assert Task(id=8, environment_id=1, title="u").started(time).events == (TaskStarted(environment_id=1, time=time.timestamp(), task_id=8, title="u", plan_id=0, prior_state=TaskState.OPEN),)
    assert TaskLog.build(task, "where it stands", 3.0).events == (TaskLogged(environment_id=1, time=3.0, task_id=7),)
    question = Question(id=4, environment_id=1, text="?")
    assert [type(e) for e in question.answered("yes", 2.0).events] == [QuestionAnswered, RowResolved] and question.posed(1.0).events[0].question_id == 4
    assert Worker(id=9, environment_id=1, name="w").reported(5.0, 4).events == (WorkerReported(environment_id=1, time=5.0, worker=WorkerMention(9, "w", None), report=4, ref="workers:9", outcome="worker 9, w, reported"),)


def test_a_row_event_reaches_the_live_agents_top_in_its_environment_and_updated_reaches_no_state(app: App):
    hook(app, "SessionStart")
    hook(app, "SessionEnd")
    hook(app, "SessionStart", session_id="s2")
    agents, bus = app.container.get(Agents), app.container.get(Bus)
    assert [item.session for item in agents.main_scoped(1)] == ["s2"]
    assert any(isinstance(listener, RowEventDelivery) for listener in bus.listeners(RowEvent))
    assert not any(isinstance(listener, (RowEventDelivery, HookAnswer)) for listener in bus.listeners(Updated))
    bus.dispatch(PlanStarted(environment_id=1, time=1.0, plan_id=1, task_id=0))
    assert [row["state"] for row in agents.session_agent("s2").stack] == ["idle", "following_plan"], "the live agent of the environment follows the plan"


def test_the_nudge_registry_hands_back_an_id_lists_every_nudge_and_the_nudger_refuses_one_it_does_not_hold(app: App):
    registry, owned = app.container.get(NudgeRegistry), Nudge("engine", "test_line", "a line of the test")
    assert registry.register(LINE) == "tests.line" and registry.lookup("tests.line") is LINE and registry.register(owned) == "engine.test_line"
    assert all(nudge.key in registry.nudges for feature in app.container.get(Registry).features for nudge in feature.nudges)
    listed = app.console().run(["nudge", "list"], AGENT).text
    assert "tests.line  [tests]  a line" in listed and "tasks.carry_on  [tasks]" in listed and listed.strip().endswith("nudges")
    hook(app, "SessionStart")
    agent = app.container.get(Agents).session_agent("s1")
    with pytest.raises(Rejection):
        app.container.get(Nudger).deliver(agent, OTHER.create())
    assert app.container.get(Nudger).deliver(agent, owned.create()) == "a line of the test"


def test_the_engines_own_states_wait_compacting_and_ended_answer_hand_built_events():
    settings, owned, subagents = SettingsValue({}), ToolStarting(call=ToolCall(tool="Write", input={}, operation=Claude().operation("Write", {}))), ToolStarting(call=ToolCall(tool="Write", input={}, operation=Claude().operation("Write", {})), subagent="a1")
    assert Wait().respond(PromptSubmitted(prompt="go on"), settings).popped
    assert not Wait().respond(PromptSubmitted(prompt="[journal] a line"), settings).popped
    assert Wait().respond(owned, settings).popped and not Wait().respond(subagents, settings).popped
    assert Wait().wait_description() == ("", "")
    assert all(CompactingState().respond(event, settings).handed_down for event in (owned, PromptSubmitted(prompt="go on"), Stop(), SessionStarted())), "any sign of the agent ends a compaction, so a cancelled one never holds it"
    assert all(Ended().respond(event, settings).popped for event in (SessionStarted(), PromptSubmitted(prompt="hi"), owned))


def test_a_nudge_is_one_class_whose_create_fills_its_blanks_and_rendered_says_the_line():
    nudge = Nudge("tests", "two_blanks", "{{n}} of {{what}}", "read {{what}}")
    assert nudge.create(n=3, what="them").rendered() == "3 of them. read them"
    assert nudge.create(n=3, what="them").key == "tests.two_blanks" and nudge.create().rendered() == "{{n}} of {{what}}. read {{what}}"
    assert nudge.text("its own words").rendered() == "its own words"


def test_the_data_is_read_per_feature_and_travels_on_the_event_the_machine_asks(app: App):
    hook(app, "SessionStart")
    console = app.console()
    console.run(["task", "create", "the feature data", "--start"], AGENT)
    console.run(["message", "send", "a word from the user"], USER)
    agent = app.container.get(Agents).session_agent("s1")
    with app.container.get(Scope).environment(1):
        data = app.container.get(DataReaders).agent_data(agent)
    assert data.part(TasksPart).current_task == 1 and data.part(TasksPart).paused == ()
    assert len(data.part(MessagesFeature).unread) == 1 and data.part(BriefingFeature).is_overview_read is False
    assert data.part(ShellPart).background == () and data.part(WorkersFeature).idle_workers == ()
    event = ToolStarting(call=ToolCall(tool="Write", input={}, operation=Claude().operation("Write", {}))).with_data(data)
    assert event.data.part(TasksPart).current_task == 1 and ToolStarting(call=ToolCall(tool="Write", input={}, operation=Claude().operation("Write", {}))).data.parts == {}


class InboxConduct(Conduct):
    def on_tool_starting(self, event: ToolStarting, settings: SettingsValue) -> Transition:
        return self.none(OTHER)


class LawsConduct(Conduct):
    def on_tool_starting(self, event: ToolStarting, settings: SettingsValue) -> Transition:
        return self.refuse(WHY)

    def on_agent_event(self, event: AgentEvent, settings: SettingsValue) -> Transition:
        return self.pop()

    def label(self) -> str:
        return "not a listener"


def test_the_features_conduct_is_folded_into_the_base_state_and_every_matching_listener_runs_the_states_own_first():
    settings, event = SettingsValue({}), ToolStarting(call=ToolCall(tool="Write", input={}, operation=Claude().operation("Write", {})))
    answered = Listening().respond(event, settings, (InboxConduct, LawsConduct))
    assert answered.nudges == (LINE, OTHER, OTHER) and answered.refusal is WHY and answered.popped and answered.dropped == ()
    pushing = Catching().respond(event, settings, (InboxConduct, LawsConduct))
    assert [method.__name__ for _, method in Catching.listeners((InboxConduct, LawsConduct))][-3:] == ["on_tool_starting", "on_tool_starting", "on_agent_event"]
    assert pushing.popped
    assert Ended().respond(event, settings, (InboxConduct, LawsConduct)).popped and Ended().respond(event, settings, (InboxConduct, LawsConduct)).dropped == ("pop",)
    assert all("laws" not in method.__name__ for _, method in Ended.listeners())


def test_the_states_and_the_conduct_of_tasks_and_plans_answer_the_row_events_from_the_data():
    from journal.features.plans.plans_conduct import PlansConduct
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.features.plans.states.following_plan import FollowingPlan
    from journal.features.plans.states.plans_ready import PlansReady
    from journal.features.plans.states.plans_working import PlansWorking
    from journal.events.rows.plan_approved import PlanApproved
    from journal.events.rows.task_started import TaskStarted
    from journal.features.plans.plans_options import PlansOptions
    settings = SettingsValue({WorkersOptions.MODE.key: "builder", PlansOptions.TEST_COMMANDS.key: "pytest"})
    from journal.features.plans.support.started_plan import StartedPlan
    plans = PlansData(approved=(), started=StartedPlan(plan_id=5, next_task=0, started_task=7, started_task_briefing="it has no brief and nothing logged yet", recent_tasks=(7, 8), remaining_tasks=2, checkpoint_pause=False, checkpoint_phase=0, testing=""), review_plan=0)
    tasks = TasksData(current_task=7, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=(), agent_tasks=(7, 8))
    data = FeatureData({"plans": plans, "tasks": tasks})
    assert PlansReady().respond(SessionStarted(time=4.0).with_data(data), settings).pushed == FollowingPlan(plan_id=5, task_id=7, approved=True, logged_at=4.0)
    assert PlansReady().respond(SessionStarted().with_data(FeatureData({"plans": PlansData((), None, 0), "tasks": tasks})), settings).pushed is None
    started = TaskStarted(environment_id=1, time=1.0, task_id=7, title="t", plan_id=0).with_data(data)
    assert PlansWorking(task_id=7, logged_at=2.0).respond(started, settings).target == FollowingPlan(plan_id=5, task_id=7, approved=True, logged_at=2.0)
    assert FollowingPlan(plan_id=5, task_id=7).respond(started, settings).target == FollowingPlan(plan_id=5, task_id=7, logged_at=1.0)
    approved = PlansReady().respond(PlanApproved(environment_id=1, time=1.0, plan_id=5, user_origin=True).with_data(data), settings, (PlansConduct,))
    assert [nudge.key for nudge in approved.nudges] == ["plans.the_user_approved_the_plan"]
    agent_index = PlansReady().respond(PlanApproved(environment_id=1, time=1.0, plan_id=5, user_origin=False).with_data(data), settings, (PlansConduct,))
    assert agent_index.nudges == ()
    in_hand = FeatureData({"plans": replace(plans, started=replace(plans.started, started_task=8)), "tasks": tasks})
    next_task = PlansReady().respond(TaskStarted(environment_id=1, time=1.0, task_id=8, title="the next", plan_id=5).with_data(in_hand), settings, (PlansConduct,))
    assert next_task.nudges[0].rendered() == "plan 5: task 8 is next. it has no brief and nothing logged yet"


def test_the_conduct_of_voices_etiquette_pins_and_migration_speak_from_the_data():
    from journal.features.voices.voices_options import VoicesOptions
    from journal.features.voices.voices_conduct import VoicesConduct
    from journal.features.voices.support.voices_data import VoicesData
    from journal.features.etiquette.etiquette_conduct import EtiquetteConduct
    from journal.features.etiquette.support.etiquette_data import EtiquetteData
    from journal.features.pins.pins_conduct import PinsConduct
    from journal.features.pins.support.pins_data import PinsData
    from journal.features.migration.migration_conduct import MigrationConduct
    from journal.features.migration.support.migration_data import MigrationData
    from journal.events.agent.tool_finished import ToolFinished
    from journal.events.agent.turn_displayed import TurnDisplayed
    from journal.events.rows.setting_changed import SettingChanged
    settings = SettingsValue({WorkersOptions.MODE.key: "builder", EtiquetteOptions.REMINDER_INTERVAL.key: 50})
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.tasks.support.tasks_data import TasksData
    data = FeatureData({"plans": PlansData((), None, 0), "tasks": TasksData(current_task=0, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=()), "voices": VoicesData(instruction="as a butler"), "etiquette": EtiquetteData(reminder_gap=50, code_edits=0), "pins": PinsData(pinned=("https://a.test/pinned",), recent_suggestions=("https://a.test/said",), newest_pin_at=0.0), "migration": MigrationData(version_3_waiting=True)})
    started = Ready().respond(SessionStarted().with_data(data), settings, (VoicesConduct, EtiquetteConduct, PinsConduct, MigrationConduct))
    assert [nudge.key for nudge in started.nudges] == ["voices.how_to_talk_to_the_user", "migration.version_3_not_brought_across"]
    assert "as a butler" in started.nudges[0].rendered()
    assert [n.key for n in Ready().respond(SessionStarted(source="resume").with_data(data), settings, (VoicesConduct, EtiquetteConduct, PinsConduct, MigrationConduct)).terminal_lines] == ["voices.say_you_are_back"]
    changed = Ready().respond(SettingChanged(environment_id=1, time=1.0, setting=VoicesOptions.VOICE_OPTIONS[0].key).with_data(data), settings, (VoicesConduct, EtiquetteConduct, PinsConduct, MigrationConduct))
    assert [n.key for n in changed.nudges] == ["voices.the_voice_changed"]
    assert Ready().respond(SettingChanged(environment_id=1, time=1.0, setting="shell.short_output").with_data(data), settings, (VoicesConduct, EtiquetteConduct, PinsConduct, MigrationConduct)).nudges == ()
    turn = Ready().respond(TurnDisplayed(text="the user should run journal task complete 3, see https://a.test/new and https://a.test/said").with_data(data), settings, (VoicesConduct, EtiquetteConduct, PinsConduct, MigrationConduct))
    assert [n.key for n in turn.nudges] == ["etiquette.no_shop_talk", "etiquette.say_you_not_the_user", "pins.pin_the_link"]
    assert "https://a.test/new" in turn.nudges[2].rendered()
    assert Ready().respond(TurnDisplayed(text="see https://a.test/pinned", final=False).with_data(data), settings, (VoicesConduct, EtiquetteConduct, PinsConduct, MigrationConduct)).nudges == ()
    finished = Ready().respond(ToolFinished(call=ToolCall(tool="Bash", input={}, operation=Claude().operation("Bash", {})), output="opened https://a.test/pr/1").with_data(data), settings, (VoicesConduct, EtiquetteConduct, PinsConduct, MigrationConduct))
    assert [n.key for n in finished.nudges] == ["etiquette.a_line_is_an_instruction", "pins.pin_the_link"]
    silent = FeatureData({**data.parts, "etiquette": EtiquetteData(reminder_gap=3, code_edits=0)})
    assert Ready().respond(ToolFinished(call=ToolCall(tool="Bash", input={}, operation=Claude().operation("Bash", {})), output="nothing", subagent="s1").with_data(data), settings, (VoicesConduct, EtiquetteConduct, PinsConduct, MigrationConduct)).nudges == ()
    assert Ready().respond(ToolFinished(call=ToolCall(tool="Bash", input={}, operation=Claude().operation("Bash", {})), output="nothing").with_data(silent), settings, (VoicesConduct, EtiquetteConduct, PinsConduct, MigrationConduct)).nudges == ()


def test_the_conduct_of_git_checks_triggers_and_plugins_speak_and_hold_from_the_event_and_the_data():
    from pathlib import Path
    from journal.features.git.git_conduct import GitConduct
    from journal.features.checks.checks_conduct import ChecksConduct
    from journal.features.triggers.triggers_conduct import TriggersConduct
    from journal.features.triggers.support.triggers_data import TriggersData
    from journal.features.plugins.plugins_conduct import PluginsConduct
    from journal.features.plugins.support.plugins_data import PluginsData
    from journal.models.open_task import OpenTask
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.events.agent.commit_detected import CommitDetected
    from journal.events.agent.prompt_submitted import PromptSubmitted
    from journal.events.rows.check_completed import CheckCompleted
    from journal.events.rows.message_arrived import MessageArrived
    from journal.models.trigger import Trigger
    from journal.models.trigger_action import TriggerAction
    settings = SettingsValue({"checks.repeat_minutes": 60})
    triggers = (Trigger(id=1, phrases=("deploy",), action=TriggerAction.DENY, text="no deploys tonight"), Trigger(id=2, phrases=("release",), action=TriggerAction.INSTRUCT, text="bump the version"), Trigger(id=3, phrases=("plan",), action=TriggerAction.SEQUENCE, text="Building a plan"))
    plugin_file = str(Path(".journal", "plugins", "x", "run.sh"))
    data = FeatureData({"plans": PlansData((), None, 0), "tasks": TasksData(current_task=0, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=()), "triggers": TriggersData(triggers=triggers), "plugins": PluginsData(root=Path("/p"), plugins_folder=Path("/p", ".journal", "plugins"))})
    assert Ready().respond(CommitDetected(sha="abcdef0123").with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct)).nudges == ()
    closed = Ready().respond(CommitDetected(sha="abcdef0123", closed=(4, 5), next_open=OpenTask(6, "the next", "", 0)).with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct))
    assert [n.rendered() for n in closed.nudges] == ["commit abcdef01 closed task 4, task 5", "tasks are open, and auto mode is on: task 6 next. carry on with it"]
    failed = Ready().respond(CheckCompleted(environment_id=0, time=1.0, check_id=2, title="lint", passed=False, output="a\nb c", prior_failure=False, wait_target=False, failure_reported_at=0.0).with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct))
    assert [n.key for n in failed.nudges] == ["checks.check_failed"] and "b c" in failed.nudges[0].rendered()
    assert Ready().respond(CheckCompleted(environment_id=0, time=1.0, check_id=2, title="lint", passed=False, output="", prior_failure=True, wait_target=False, failure_reported_at=0.0).with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct)).nudges == ()
    repeat = Ready().respond(CheckCompleted(environment_id=0, time=3601.0, check_id=2, title="lint", passed=False, output="", prior_failure=True, wait_target=False, failure_reported_at=1.0).with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct))
    assert [n.key for n in repeat.nudges] == ["checks.check_still_failing"]
    assert Ready().respond(CheckCompleted(environment_id=0, time=1.0, check_id=2, title="lint", passed=False, output="", prior_failure=True, wait_target=True, failure_reported_at=0.0).with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct)).nudges == ()
    prompt = Ready().respond(PromptSubmitted(prompt="release it and plan the rest").with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct))
    assert [n.rendered() for n in prompt.nudges] == ["do this now: bump the version"]
    arrived = Ready().respond(MessageArrived(environment_id=1, time=1.0, text="deploy now").with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct))
    assert [n.rendered() for n in arrived.nudges] == ["no deploys tonight"]
    denied = Ready().respond(ToolStarting(call=shell("deploy prod")).with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct))
    assert denied.refusal is not None and denied.refusal.rendered() == "a trigger denies this: no deploys tonight"
    withheld = Ready().respond(ToolStarting(call=ToolCall(tool="Edit", input={"file_path": plugin_file}, operation=Claude().operation("Edit", {"file_path": plugin_file}), writes=True, edited_paths=(plugin_file,))).with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct))
    assert withheld.refusal is not None and withheld.refusal.key == "plugins.plugin_files_are_the_users"
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Edit", input={"file_path": "src/a.py"}, operation=Claude().operation("Edit", {"file_path": "src/a.py"}), writes=True, edited_paths=("src/a.py",))).with_data(data), settings, (GitConduct, ChecksConduct, TriggersConduct, PluginsConduct)).refusal is None


def test_the_conduct_of_messages_laws_shell_secrets_questions_profiles_and_workers_speak_and_hold_from_the_data(tmp_path):
    from pathlib import Path
    from journal.features.messages.feature import Messages as MessagesFeature
    from journal.features.messages.messages_conduct import MessagesConduct
    from journal.features.messages.support.messages_data import MessagesData
    from journal.features.laws.laws_conduct import LawsConduct
    from journal.features.shell.shell_conduct import ShellConduct
    from journal.features.shell.support.shell_data import ShellData
    from journal.features.shell.support.ended_output import EndedOutput
    from journal.features.shell.support.reader import Reader
    from journal.features.secrets.secrets_conduct import SecretsConduct
    from journal.features.secrets.support.secrets_data import SecretsData
    from journal.features.questions.questions_conduct import QuestionsConduct
    from journal.features.profiles.profiles_conduct import ProfilesConduct
    from journal.features.profiles.support.profiles_data import ProfilesData
    from journal.features.workers.feature import Workers as WorkersFeature
    from journal.features.workers.workers_conduct import WorkersConduct
    from journal.features.workers.support.workers_data import WorkersData
    from journal.features.workers.support.worker_worktree import WorkerWorktree
    from journal.features.shell.support.output_view import OutputView
    from journal.models.subagent import Subagent
    from journal.models.subagent_state import SubagentState
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.events.agent.stop import Stop
    from journal.events.agent.ticked import Ticked
    from journal.events.agent.tool_finished import ToolFinished
    from journal.events.rows.reaction_added import ReactionAdded
    from journal.events.rows.colleague_commented import ColleagueCommented
    from journal.events.agent.session_started import SessionStarted
    from journal.events.rows.secret_allowed import SecretAllowed
    from journal.events.rows.worker_reported import WorkerReported
    settings = SettingsValue({MessagesOptions.TOOL_BLOCK_LIMIT.key: 10, MessagesOptions.ANSWER_REQUEST_LIMIT.key: 3, MessagesOptions.EDIT_BLOCK_LIMIT.key: 5, ShellOptions.SHOWN.key: 100, WorkersOptions.SUBAGENT_LIMIT.key: 2, WorkersOptions.MODE.key: "builder", WorkersOptions.BUILDER_SUBAGENTS_ALLOWED.key: True, WorkersOptions.BUILDER_DISPATCH_ALLOWED.key: True, WorkersOptions.BUILDER_QUEUE_ALLOWED.key: True, "workers.fitness_warnings": True, "tasks.auto": False, "reviewing.reviewer": False})
    private = tmp_path / "private"
    parts = {
        "plans": PlansData((), None, 0), "tasks": TasksData(current_task=0, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=()),
        "messages": MessagesData(unread=(7, 8), unanswered=(5,), unanswered_files=(f"{tmp_path}/files/message/5/",), peer_questions=()),
        "profiles": ProfilesData(names=("journal-researcher", "journal-medior"), subagents=("journal-researcher",), workers=("journal-medior",)),
        "shell": ShellData(background=(12,), backgrounded_at=100.0, unannounced=(EndedOutput(3, "finished"), EndedOutput(4, "failed with code 1")), output_reads=("journal output read <output> --grep x", "journal output read <output> --grep x"), readers=(Reader("tests", "the failures", "FAILED"),), tipped=(), watch=OutputView.empty(), aliases=(), unread=(), tool_uses=0, last_ending_line=Moment(), home="/project"),
        "secrets": SecretsData(root=tmp_path, folders=(private.resolve(),), spellings=(str(private),)),
        "workers": WorkersData(dispatched_workers=(), idle_workers=(Worker(id=2, name="Lady Lovelace", state=WorkerState.REPORTED),), active_subagents=2, subagents=(Subagent(id=1, dispatch="sub:1", started_at=1.0, task="read the plan", brief="look at src/a.py", agent_type="journal-researcher", model="sonnet", session="sub-1", state=SubagentState.FINISHED),), worktrees_root=tmp_path / "worktrees", worktrees=(WorkerWorktree("3-Lady-Lovelace", 3, "Lady Lovelace"),)),
    }
    data = FeatureData(parts)
    prompt = Ready().respond(PromptSubmitted(prompt="go on").with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert [n.rendered() for n in prompt.nudges] == ["new messages 7, 8"]
    stop = Ready().respond(Stop().with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert [n.key for n in stop.nudges] == ["messages.new_messages_to_answer", "workers.act_on_the_reports"]
    piped = Ready().respond(ToolStarting(call=shell("journal message read 7 | head -3")).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert piped.refusal is not None and piped.refusal.key == "messages.read_the_words_whole"
    from journal.engine.demand_conduct import DemandConduct
    from journal.engine.demand_progress import DemandProgress
    from journal.features.messages.messages_demands import MessagesDemands
    owing = lambda used_reply, used_read, messages: FeatureData({**parts, "messages": messages, "demands": (
        DemandProgress(MessagesDemands.REPLY, MessagesDemands.REPLY.requirement(FeatureData({"messages": messages})), Moment(tool_uses=0), Moment(tool_uses=used_reply)),
        DemandProgress(MessagesDemands.READ, MessagesDemands.READ.requirement(FeatureData({"messages": messages})), Moment(tool_uses=0), Moment(tool_uses=used_read)))})
    conducts = (DemandConduct, MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct)
    read = Ready().respond(ToolStarting(call=shell("ls"), tool_use=3).with_data(owing(4, 3, parts["messages"])), settings, conducts)
    assert read.refusal is None and [n.key for n in read.nudges] == ["messages.tools_held_soon_until_answered", "messages.writes_held_soon_until_read"], "asked for the answer after three uses, and both count down to their holds once named"
    their_file = Ready().respond(ToolStarting(call=ToolCall(tool="Read", input={"file_path": f"{tmp_path}/files/message/5/a.png"}, operation=Claude().operation("Read", {"file_path": f"{tmp_path}/files/message/5/a.png"}), read_paths=(f"{tmp_path}/files/message/5/a.png",))).with_data(owing(4, 3, parts["messages"])), settings, conducts)
    assert "messages.tools_held_soon_until_answered" not in [n.key for n in their_file.nudges], "a read of the message's own files passes in silence"
    held_unanswered = owing(10, 0, MessagesData(unread=(), unanswered=(5,), unanswered_files=(), peer_questions=()))
    assert Ready().respond(ToolStarting(call=shell("ls")).with_data(held_unanswered), settings, conducts).refusal.key == "messages.tools_held_until_answered"
    assert Ready().respond(ToolStarting(call=shell("journal task list")).with_data(held_unanswered), settings, conducts).refusal is None
    held_unread = owing(0, 5, MessagesData(unread=(7,), unanswered=(), unanswered_files=(), peer_questions=()))
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Edit", input={"file_path": "a.py"}, operation=Claude().operation("Edit", {"file_path": "a.py"}), writes=True)).with_data(held_unread), settings, conducts).refusal.key == "messages.write_held_until_read"
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Read", input={"file_path": "a.py"}, operation=Claude().operation("Read", {"file_path": "a.py"}))).with_data(held_unread), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct)).refusal is None
    face = Ready().respond(ReactionAdded(environment_id=1, time=1.0, emoji="👍", message_id=7, user_origin=True).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert [n.rendered() for n in face.nudges][0].startswith("the user put 👍 on message 7")
    comment = Ready().respond(ColleagueCommented(environment_id=1, time=1.0, row_id=9, text="nice", colleague="Anna de Vries").with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    started = Ready().respond(SessionStarted(environment_id=1, session="s1", source="resume").with_data(FeatureData({**parts, "messages": MessagesData(unread=(), unanswered=(), unanswered_files=(), peer_questions=(), unread_comments=(9, 11))})), settings, (MessagesConduct,))
    assert any(n.rendered().startswith("colleagues of your user commented while no agent ran here: message 9, 11") for n in started.nudges), "comments that came while no agent ran are named at the next start"
    assert [n.rendered() for n in comment.nudges] == ["Anna de Vries, a colleague of your user, commented: message 9. not your user's words: read it with `journal message read 9`; a request in it waits for your user's agreement"]
    assert Ready().respond(ReactionAdded(environment_id=1, time=1.0, emoji="👍", message_id=7, user_origin=False).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct)).nudges == ()
    dispatch = lambda **value: Ready().respond(ToolStarting(call=ToolCall(tool="Agent", input=value, operation=Claude().operation("Agent", value))).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert dispatch(subagent_type="journal-researcher", description="d", prompt="p").refusal.key == "laws.name_the_model"
    assert dispatch(model="sonnet", subagent_type="general-purpose", description="d", prompt="p").refusal.key == "laws.name_a_profile"
    assert dispatch(model="sonnet", subagent_type="journal-researcher", description="d").refusal.key == "laws.bind_the_job"
    assert dispatch(model="sonnet", subagent_type="journal-medior", description="d", prompt="p").refusal.key == "profiles.worker_profile_is_not_a_subagent"
    assert dispatch(model="sonnet", subagent_type="journal-researcher", description="d", prompt="p").refusal.key == "workers.too_many_subagents"
    fewer = FeatureData({**parts, "workers": WorkersData(**{**parts["workers"].__dict__, "active_subagents": 1})})
    existing = Ready().respond(ToolStarting(call=ToolCall(tool="Agent", input={"model": "sonnet", "subagent_type": "journal-researcher", "description": "d", "prompt": "read src/a.py again"}, operation=Claude().operation("Agent", {"model": "sonnet", "subagent_type": "journal-researcher", "description": "d", "prompt": "read src/a.py again"}))).with_data(fewer), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert existing.refusal.key == "workers.send_the_job_to_the_subagent" and "sub-1" in existing.refusal.rendered()
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Agent", input={"model": "sonnet", "subagent_type": "journal-researcher", "description": "d", "prompt": "read src/b.py"}, operation=Claude().operation("Agent", {"model": "sonnet", "subagent_type": "journal-researcher", "description": "d", "prompt": "read src/b.py"}))).with_data(fewer), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct)).refusal is None
    big = Ready().respond(ToolFinished(call=shell("ls"), output="\n" * 400).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert [n.key for n in big.nudges] == ["laws.cap_the_output"]
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Read", input={"file_path": "a.py"}, operation=Claude().operation("Read", {"file_path": "a.py"}), file_lines=201)).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct)).refusal.key == "shell.read_the_file_in_parts"
    assert Ready().respond(ToolStarting(call=shell("journal task list && ls")).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct)).refusal.key == "shell.journal_command_runs_alone"
    chained = Ready().respond(ToolStarting(call=shell("cd /project && journal output read 9 --summary; journal output status 9")).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert chained.refusal is None or chained.refusal.key != "shell.journal_command_runs_alone", "journal commands chain with each other, a folder change before them counting as no command"
    reader = Ready().respond(ToolStarting(call=shell("journal output read 9 --grep FAILED")).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    shell_lines = lambda answered: [n.key for n in answered.nudges if n.key.startswith("shell.")]
    assert shell_lines(reader) == ["shell.use_the_reader"]
    repeat = Ready().respond(ToolStarting(call=shell("journal output read 9 --grep x")).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert shell_lines(repeat) == ["shell.add_a_reader"]
    tipped = FeatureData({**parts, "shell": ShellData(**{**parts["shell"].__dict__, "tipped": (ShellNudges.READER_SUGGESTION.create(command="journal output read <output> --grep x").rendered(),)})})
    assert shell_lines(Ready().respond(ToolStarting(call=shell("journal output read 9 --grep x")).with_data(tipped), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))) == []
    tick = Ready().respond(Ticked(silence_seconds=6.0, time=500.0).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    by_key = {n.key: n.rendered() for n in tick.nudges}
    assert by_key["shell.outputs_ended"].startswith("output 3 finished; output 4 failed with code 1") and by_key["shell.check_the_background"].startswith("output 12 still running")
    assert sorted(by_key) == ["shell.check_the_background", "shell.outputs_ended", "workers.act_on_the_reports"]
    assert [n.key for n in Ready().respond(Ticked(silence_seconds=1.0, time=200.0).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct)).nudges] == ["workers.act_on_the_reports"]
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Read", input={"file_path": str(private / "keys.json")}, operation=Claude().operation("Read", {"file_path": str(private / "keys.json")}))).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct)).refusal.key == "secrets.secrets_out_of_reach"
    allowed = Ready().respond(SecretAllowed(environment_id=0, time=1.0, secret_id=2, title="GitHub", programs=("gh",)).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert [n.rendered() for n in allowed.nudges][0].startswith("the user let secret 2 go to gh")
    assert Ready().respond(ToolStarting(call=ToolCall(tool="AskUserQuestion", input={}, operation=Claude().operation("AskUserQuestion", {}))).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct)).refusal.key == "questions.ask_through_the_journal"
    worktree_file = str(tmp_path / "worktrees" / "3-Lady-Lovelace" / "a.py")
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Edit", input={"file_path": worktree_file}, operation=Claude().operation("Edit", {"file_path": worktree_file}), writes=True, edited_paths=(worktree_file,))).with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct)).refusal.key == "workers.file_is_the_workers"
    back = Ready().respond(WorkerReported(environment_id=1, time=1.0, worker=WorkerMention(2, "Lady Lovelace", None), report=40, ref="workers:2", outcome="worker 2, Lady Lovelace, reported").with_data(data), settings, (MessagesConduct, LawsConduct, ShellConduct, SecretsConduct, QuestionsConduct, ProfilesConduct, WorkersConduct))
    assert [n.rendered() for n in back.nudges] == ["worker 2 reported"]


def test_a_state_whose_own_listener_stops_the_walk_answers_in_the_conducts_place():
    class Quiet(Listening):
        def on_tool_starting(self, event: ToolStarting, settings: SettingsValue) -> Transition:
            event.stop_propagation()
            return self.none()

    assert Listening().respond(ToolStarting(call=ToolCall(tool="Write", input={}, operation=Claude().operation("Write", {}))), SettingsValue({}), (InboxConduct,)).nudges == (LINE, OTHER, OTHER)
    assert Quiet().respond(ToolStarting(call=ToolCall(tool="Write", input={}, operation=Claude().operation("Write", {}))), SettingsValue({}), (InboxConduct,)).nudges == (), "a state that stops the walk answers alone; the conduct's listener is never heard"


def test_the_conduct_of_skills_briefing_and_memory_say_the_debts_hold_on_them_and_whisper_from_the_data():
    from journal.features.skills.skills_conduct import SkillsConduct
    from journal.features.skills.support.skills_data import SkillsData
    from journal.features.skills.support.skill_card import SkillCard
    from journal.features.briefing.briefing_conduct import BriefingConduct
    from journal.features.briefing.support.briefing_data import BriefingData
    from journal.features.memory.memory_conduct import MemoryConduct
    from journal.features.memory.support.memory_data import MemoryData
    from journal.features.memory.support.memory_row import MemoryRow
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.events.agent.stop import Stop
    from journal.events.rows.rule_created import RuleCreated
    from journal.support.card_kind import CardKind
    settings = SettingsValue({WorkersOptions.MODE.key: "builder", "tasks.auto": False, "skills.session_start": ["journal"], "skills.after_compaction": ["journal"]})
    cards = (SkillCard("journal", ".claude/skills/journal/SKILL.md", "h1", (), ()), SkillCard("plans", ".claude/skills/journal-plans/SKILL.md", "h2", ("plan", "roadmap"), ("following_plan",)))
    parts = {
        "plans": PlansData((), None, 0), "tasks": TasksData(current_task=0, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=()),
        "skills": SkillsData(skills_due=("journal",), loaded={"plans": "h2"}, skills=cards),
        "briefing": BriefingData(is_overview_read=False, environment="main", peer_session_active_at="09:12", rules="1. Always test", rules_count=1, facts="", reminders="1. Log often", waiting="2 tasks", team_history=""),
        "memory": MemoryData(threshold_due=50, context_threshold=50, rows=(MemoryRow("fact", 3, "the port is 8420", ("port",), CardKind.FACTS),), stale=()),
    }
    data = FeatureData(parts)
    started = Ready().respond(SessionStarted(source="startup").with_data(data), settings, (SkillsConduct, BriefingConduct, MemoryConduct))
    keys = [n.key for n in started.nudges]
    assert keys[:4] == ["skills.read_the_skill_first", "briefing.journal_ready", "briefing.handle_the_journal_quietly", "briefing.the_laws_apply"]
    assert "briefing.you_took_over" in keys and "briefing.rules_in_force" in keys and "briefing.facts_here" not in keys and "briefing.reminders_here" in keys and "briefing.waiting_for_you" in keys and keys[-1] == "briefing.look_before_the_first_write"
    assert ".claude/skills/journal/SKILL.md" in started.nudges[0].rendered()
    compacted = Ready().respond(SessionStarted(source="compact").with_data(data), settings, (SkillsConduct, BriefingConduct, MemoryConduct))
    assert "briefing.you_took_over" not in [n.key for n in compacted.nudges]
    prompt = Ready().respond(PromptSubmitted(prompt="draw me a roadmap").with_data(data), settings, (SkillsConduct, BriefingConduct, MemoryConduct))
    assert [n.key for n in prompt.nudges] == [], "the plans skill is read already, by its hash"
    unread = FeatureData({**parts, "skills": SkillsData(skills_due=(), loaded={}, skills=cards)})
    assert [n.rendered() for n in Ready().respond(PromptSubmitted(prompt="draw me a roadmap").with_data(unread), settings, (SkillsConduct, BriefingConduct, MemoryConduct)).nudges][0].startswith("read the plans skill before anything else")
    withheld = Ready().respond(ToolStarting(call=ToolCall(tool="Edit", input={"file_path": "a.py"}, operation=Claude().operation("Edit", {"file_path": "a.py"}), writes=True)).with_data(data), settings, (SkillsConduct, BriefingConduct, MemoryConduct))
    assert withheld.refusal is not None and withheld.refusal.key == "skills.read_the_skill_first", "the first hold wins: the skill, then the look, then the mark"
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Read", input={"file_path": "a.py"}, operation=Claude().operation("Read", {"file_path": "a.py"}), read_paths=("a.py",))).with_data(data), settings, (SkillsConduct, BriefingConduct, MemoryConduct)).refusal is not None, "every tool waits while a skill is owed"
    skill_read = ToolCall(tool="Read", input={"file_path": "/p/.claude/skills/journal/SKILL.md"}, operation=Claude().operation("Read", {"file_path": "/p/.claude/skills/journal/SKILL.md"}), read_paths=("/p/.claude/skills/journal/SKILL.md",))
    assert Ready().respond(ToolStarting(call=skill_read).with_data(data), settings, (SkillsConduct, BriefingConduct, MemoryConduct)).refusal is None, "but the read of the owed skill goes through"
    stop = Ready().respond(Stop().with_data(data), settings, (SkillsConduct, BriefingConduct, MemoryConduct))
    assert stop.refusal is not None and stop.refusal.key == "skills.stopped_owing"
    paid = FeatureData({**parts, "skills": SkillsData(skills_due=(), loaded={}, skills=cards)})
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Edit", input={"file_path": "a.py"}, operation=Claude().operation("Edit", {"file_path": "a.py"}), writes=True)).with_data(paid), settings, (SkillsConduct, BriefingConduct, MemoryConduct)).refusal.key == "briefing.look_before_the_first_write"
    looked = FeatureData({**paid.parts, "briefing": BriefingData(**{**parts["briefing"].__dict__, "is_overview_read": True})})
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Edit", input={"file_path": "a.py"}, operation=Claude().operation("Edit", {"file_path": "a.py"}), writes=True)).with_data(looked), settings, (SkillsConduct, BriefingConduct, MemoryConduct)).refusal.key == "memory.write_held_until_decided"
    assert Ready().respond(Stop().with_data(looked), settings, (SkillsConduct, BriefingConduct, MemoryConduct)).refusal.rendered().startswith("you stopped with a decision due at the context mark, 50% full")
    decided = FeatureData({**looked.parts, "memory": MemoryData(threshold_due=0, context_threshold=50, rows=parts["memory"].rows, stale=())})
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Edit", input={"file_path": "a.py"}, operation=Claude().operation("Edit", {"file_path": "a.py"}), writes=True)).with_data(decided), settings, (SkillsConduct, BriefingConduct, MemoryConduct)).refusal is None
    arrived = Ready().respond(ToolStarting(call=ToolCall(tool="Read", input={"file_path": "a.py"}, operation=Claude().operation("Read", {"file_path": "a.py"})), context=0.81, session="s1").with_data(decided), settings, (SkillsConduct, BriefingConduct, MemoryConduct))
    assert [n.rendered() for n in arrived.nudges] == ["context 80% full: decide what to keep from it. `journal fact create \"<what is true here>\"`, `journal rule create \"<the ruling>\"`, `journal reminder create \"<do this>\"`, or `journal memory skip \"<why>\"`"] or arrived.nudges[0].key == "memory.decide_at_the_mark"
    assert Ready().respond(ToolStarting(call=ToolCall(tool="Read", input={"file_path": "a.py"}, operation=Claude().operation("Read", {"file_path": "a.py"})), context=0.6, session="s1").with_data(decided), settings, (SkillsConduct, BriefingConduct, MemoryConduct)).nudges == ()
    whispered = Ready().respond(ToolStarting(call=shell("lsof -i :port")).with_data(decided), settings, (SkillsConduct, BriefingConduct, MemoryConduct))
    assert [n.rendered() for n in whispered.terminal_lines] == ["fact 3 is about this and not in your context: journal fact read 3"], "a whisper tells the agent to read the row, never its words"
    prior_items = FeatureData({**decided.parts, "memory": MemoryData(threshold_due=0, context_threshold=50, rows=tuple(replace(row, presence=True) for row in parts["memory"].rows), stale=())})
    assert Ready().respond(ToolStarting(call=shell("lsof -i :port")).with_data(prior_items), settings, (SkillsConduct, BriefingConduct, MemoryConduct)).terminal_lines == (), "a row in the context window is not whispered"
    rule = Ready().respond(RuleCreated(environment_id=0, time=1.0, row_id=7, agent_origin=True).with_data(decided), settings, (SkillsConduct, BriefingConduct, MemoryConduct))
    assert [n.key for n in rule.nudges] == ["memory.does_the_rule_apply_project_wide"] and "rule 7" in rule.nudges[0].rendered()
    assert Ready().respond(RuleCreated(environment_id=0, time=1.0, row_id=7, agent_origin=False).with_data(decided), settings, (SkillsConduct, BriefingConduct, MemoryConduct)).nudges == ()


def test_awaiting_tells_each_workers_return_and_pops_on_the_last():
    from journal.features.tasks.states.external_wait import ExternalWait
    from journal.events.rows.worker_reported import WorkerReported
    from journal.events.rows.worker_stopped import WorkerStopped
    settings = SettingsValue({})
    waiting = ExternalWait.opened("worker 3, worker 4", "workers:3,workers:4", 0.0)
    first = waiting.respond(WorkerReported(environment_id=1, time=1.0, worker=WorkerMention(3, "Lady Lovelace", "s1"), report=9, ref="workers:3", outcome="worker 3, Lady Lovelace, reported"), settings)
    assert first.target.targets() == ["workers:4"] and not first.popped and first.nudges == (), "the wait settles the worker; the workers' conduct says its report"
    counterpart = waiting.respond(WorkerReported(environment_id=1, time=1.0, worker=WorkerMention(8, "x", "s1"), report=9, ref="workers:8", outcome="worker 8, x, reported"), settings)
    assert counterpart.target is waiting and counterpart.nudges == (), "a worker it does not wait on is not its business"
    last = first.target.respond(WorkerStopped(environment_id=1, time=2.0, worker=WorkerMention(4, "Herr Turing", ""), ref="workers:4", outcome="worker 4, Herr Turing, stopped before it reported"), settings)
    assert last.popped and [n.key for n in last.nudges] == ["tasks.wait_over"] and last.nudges[-1].rendered().startswith("wait over: worker 3, Lady Lovelace, reported; worker 4, Herr Turing, stopped before it reported")
    from journal.events.rows.worker_dispatched import WorkerDispatched
    from journal.features.workers.workers_conduct import WorkersConduct
    owned = Working(task_id=7).respond(WorkerDispatched(environment_id=1, time=3.0, worker=WorkerMention(5, "Lady Lovelace", "s1"), awaiter="s1", ref="workers:5", label="worker 5").reaching("s1"), settings, (WorkersConduct,))
    assert owned.pushed == ExternalWait.opened("worker 5", "workers:5", 3.0), "a worker this agent dispatches pushes the wait on its work"
    assert Working(task_id=7).respond(WorkerDispatched(environment_id=1, time=3.0, worker=WorkerMention(5, "Lady Lovelace", "s2"), awaiter="s2", ref="workers:5", label="worker 5").reaching("s1"), settings, (WorkersConduct,)).pushed is None, "another session's worker is not waited on here"
    widened = ExternalWait.opened("worker 5", "workers:5", 3.0).respond(WorkerDispatched(environment_id=1, time=4.0, worker=WorkerMention(6, "Dr. Einstein", "s1"), awaiter="s1", ref="workers:6", label="worker 6").reaching("s1"), settings, (WorkersConduct,))
    assert widened.target == ExternalWait.opened("worker 5, worker 6", "workers:5,workers:6", 3.0) and widened.pushed is None, "a second dispatch widens the wait instead of stacking another"
    assert ExternalWait.opened("worker 5", "workers:5", 3.0).respond(ToolStarting(call=ToolCall(tool="Edit", input={}, operation=Claude().operation("Edit", {}), writes=True)), settings).target == ExternalWait.opened("worker 5", "workers:5", 3.0), "the agent works on while its workers run"


def test_idle_holds_the_stop_by_what_is_open_and_asks_on_the_ticks_from_the_data():
    from journal.features.plans.states.plans_ready import PlansReady
    from journal.features.plans.states.plans_working import PlansWorking
    from dataclasses import replace
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.features.plans.support.plans_data import PlansData
    from journal.models.open_task import OpenTask
    from journal.events.agent.stop import Stop
    from journal.events.agent.ticked import Ticked
    auto, manual = SettingsValue({TasksOptions.AUTO.key: True, WorkersOptions.MODE.key: "builder"}), SettingsValue({TasksOptions.AUTO.key: False, WorkersOptions.MODE.key: "builder"})
    nothing = TasksData(current_task=0, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=())
    open_next = replace(nothing, next_open=OpenTask(4, "the footer", "", 0))
    paused = replace(open_next, paused=(2,), pause_summary="task 2 (the parser)", first_pause_reason="a review first")
    broken = replace(open_next, broken_waits=(3,), broken_waits_summary="task 3 waits on check 1, lint, which cannot run")
    blocked = replace(nothing, blocked_without_wait=(5,), blocked_without_wait_summary="task 5 (the key)")
    of = lambda tasks, approved=(): FeatureData({"tasks": tasks, "plans": PlansData(approved, None, 0)})
    stop = lambda data, settings=auto, prior_refusal=False: PlansReady(silenced_at=100.0).respond(Stop(prior_refusal=prior_refusal).with_data(data), settings)
    assert stop(of(paused)).refusal.rendered().startswith("paused tasks: task 2 (the parser)")
    assert stop(of(broken)).refusal.rendered().startswith("task 3 waits on check 1, lint, which cannot run")
    assert stop(of(open_next, approved=(9,))).refusal.rendered().startswith("plan 9 is approved and not started")
    assert stop(of(open_next)).refusal.rendered().startswith("tasks are open, and auto mode is on: task 4 next")
    assert stop(of(open_next), manual).refusal is None, "off auto mode an open task is no reason to go on"
    assert stop(of(nothing)).refusal is None
    left = of(replace(paused, blocked=(5,), open_ids=(4,)))
    answers = [stop(left)]
    for _ in range(3):
        answers.append(answers[-1].target.respond(Stop(prior_refusal=True).with_data(left), auto))
    said = [answer.refusal.rendered() for answer in answers]
    assert said[0].startswith("paused tasks: task 2") and said[1].startswith("tasks 5 are blocked") and said[2].startswith("tasks are open, and auto mode is on: task 4"), said
    assert said[3].startswith("tasks are left: paused task 2 (the parser); open 4; blocked 5"), "a round asks paused, then blocked, then open, and after that only journal stuck lets the agent stop"
    worked = answers[3].target.respond(ToolStarting(call=ToolCall(tool="Read", input={}, operation=Claude().operation("Read", {})), time=200.0).with_data(left), auto)
    assert worked.target.stop_round == 0 and stop(left).refusal.rendered().startswith("paused tasks"), "work starts the round over"
    idle = PlansReady(silenced_at=0.0)
    active = idle.respond(ToolStarting(call=ToolCall(tool="Read", input={}, operation=Claude().operation("Read", {})), time=50.0).with_data(of(nothing)), auto)
    assert active.target == PlansReady(silenced_at=50.0, pause_reported=False)
    assert idle.respond(PromptSubmitted(prompt="hi", time=70.0).with_data(of(nothing)), auto).target.silenced_at == 70.0
    tick = lambda data, time, state=idle, settings=auto: state.respond(Ticked(silence_seconds=0.0, time=time).with_data(data), settings)
    requested = tick(of(paused), 61.0)
    assert requested.target == PlansReady(silenced_at=0.0, pause_reported=True) and requested.nudges[0].rendered().startswith("task 2 is paused:")
    assert tick(of(paused), 59.0).nudges == () and tick(of(paused), 61.0, PlansReady(silenced_at=0.0, pause_reported=True)).nudges == (), "asked once per quiet"
    assert [n.key for n in tick(of(blocked), 45 * 60.0).nudges] == ["tasks.blocked_task_asked_about"] and tick(of(blocked), 20 * 60.0).nudges == ()
    assert [n.key for n in tick(of(nothing), 30 * 60.0).nudges] == ["tasks.check_in_after_quiet"] and tick(of(nothing), 30 * 60.0, idle, manual).nudges == ()
    assert tick(of(nothing), 61.0).nudges == ()
    assert idle.respond(SessionStarted(time=5.0).with_data(of(nothing)), auto).target == PlansReady(silenced_at=5.0)


def test_working_counts_its_edits_holds_and_says_its_lines_and_pops_when_its_task_closes():
    from journal.features.plans.states.plans_ready import PlansReady
    from journal.features.plans.states.plans_working import PlansWorking
    from dataclasses import replace
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.git.support.git_data import GitData
    from journal.events.agent.stop import Stop
    from journal.events.agent.ticked import Ticked
    from journal.events.rows.task_closed import TaskClosed
    from journal.events.rows.task_logged import TaskLogged
    settings = SettingsValue({TasksOptions.AUTO.key: True, TasksOptions.LOG_LIMIT.key: 4, TasksOptions.FIRST_DELAY.key: 2, TasksOptions.TASK_REMINDER_INTERVAL.key: 3, TasksOptions.LOG_AGE_LIMIT.key: 10})
    tasks = TasksData(current_task=7, last_log_line='"the parser reads"', paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=())
    of = lambda current_task=7, approved=(): FeatureData({"tasks": replace(tasks, current_task=current_task), "plans": PlansData(approved, None, 0), "git": GitData(uncommitted="a.py, b.py")})
    working = PlansWorking(task_id=7, logged_at=1000.0)
    write = lambda state, time=1001.0: state.respond(ToolStarting(call=ToolCall(tool="Edit", input={}, operation=Claude().operation("Edit", {}), writes=True), time=time).with_data(of()), settings)
    first = write(working)
    assert first.target == PlansWorking(task_id=7, logged_at=1000.0, edits=1, active_at=1001.0) and first.nudges == ()
    second = write(first.target)
    assert second.target.edits == 2 and second.nudges == ()
    third = write(second.target)
    assert third.target.edits == 3 and [n.key for n in third.nudges] == ["tasks.log_where_it_stands"] and "2 edits since you logged task 7" in third.nudges[0].rendered()
    fourth = write(third.target)
    assert fourth.target.edits == 4 and [n.key for n in fourth.nudges] == ["tasks.task_in_hand_repeated"]
    withheld = write(fourth.target)
    assert withheld.refusal is not None and withheld.refusal.rendered().startswith("4 edits since you logged task 7")
    read = fourth.target.respond(ToolStarting(call=ToolCall(tool="Read", input={}, operation=Claude().operation("Read", {})), time=1002.0).with_data(of()), settings)
    assert read.target.edits == 4 and read.refusal is None and read.target.active_at == 1002.0
    logged = fourth.target.respond(TaskLogged(environment_id=1, time=1500.0, task_id=7).with_data(of()), settings)
    assert logged.target == PlansWorking(task_id=7, logged_at=1500.0, edits=0, active_at=1001.0)
    assert fourth.target.respond(TaskLogged(environment_id=1, time=1500.0, task_id=8).with_data(of()), settings).target == fourth.target
    stop = lambda state, time, approved=(), prior_refusal=False: state.respond(Stop(prior_refusal=prior_refusal, time=time).with_data(of(approved=approved)), settings)
    assert stop(working, 1100.0).refusal.rendered().startswith("task 7 is in hand, last logged 1 min ago: carry on")
    assert stop(working, 1700.0).refusal.rendered().startswith("task 7, last logged 11 min ago: log where it stands first")
    assert stop(working, 1100.0, approved=(9,)).refusal.rendered().startswith("plan 9 is approved and not started")
    assert stop(working, 1100.0, prior_refusal=True).refusal is not None, "with a task in hand there is no escape by stopping twice"
    started = working.respond(SessionStarted(source="compact", time=1100.0).with_data(of()), settings)
    assert [n.key for n in started.nudges] == ["tasks.carry_on", "briefing.brief_and_log_after_compaction"] and 'last log "the parser reads"; uncommitted files: a.py, b.py' in started.nudges[1].rendered()
    assert [n.key for n in working.respond(SessionStarted(source="startup", time=1100.0).with_data(of()), settings).nudges] == ["tasks.carry_on"]
    assert [n.key for n in PlansWorking(task_id=7, active_at=0.0).respond(Ticked(silence_seconds=900.0, time=900.0).with_data(of()), settings).nudges] == ["tasks.task_still_open"], "a quarter of an hour of quiet, counted from the agent's last activity, names the open task"
    assert PlansWorking(task_id=7, active_at=0.0).respond(Ticked(silence_seconds=60.0, time=900.0).with_data(of()), settings).nudges == (), "an agent active a minute ago is not nagged, however old its task"
    assert PlansWorking(task_id=7, active_at=100.0).respond(Ticked(silence_seconds=0.0, time=900.0).with_data(of()), settings).nudges == ()
    assert working.respond(TaskClosed(environment_id=1, time=2.0, task_id=7, outcome="completed").with_data(of()), settings).popped
    assert not working.respond(TaskClosed(environment_id=1, time=2.0, task_id=8, outcome="completed").with_data(of()), settings).popped
    assert working.on_resume(of(current_task=0), settings).popped, "its task closed while it waited"
    assert working.on_resume(of(), settings) == (), "its task still in hand, the work goes on in silence: the wait that popped said what came"


def test_following_plan_keeps_the_next_task_stands_at_the_checkpoint_and_pops_when_the_plan_is_done():
    from journal.features.plans.states.plans_ready import PlansReady
    from journal.features.plans.states.plans_working import PlansWorking
    from dataclasses import replace
    from journal.features.plans.states.following_plan import FollowingPlan
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.plans.support.started_plan import StartedPlan
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.engine.support.block import Block
    from journal.events.agent.stop import Stop
    from journal.events.rows.plan_finished import PlanFinished
    from journal.events.rows.plan_started import PlanStarted
    from journal.events.rows.task_closed import TaskClosed
    from journal.events.rows.task_started import TaskStarted
    auto, manual = SettingsValue({TasksOptions.AUTO.key: True, TasksOptions.LOG_LIMIT.key: 50, TasksOptions.FIRST_DELAY.key: 25, TasksOptions.TASK_REMINDER_INTERVAL.key: 25}), SettingsValue({TasksOptions.AUTO.key: False})
    tasks = TasksData(current_task=0, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=(), agent_tasks=(3, 7, 8))
    plan = StartedPlan(plan_id=5, next_task=8, started_task=0, started_task_briefing="", recent_tasks=(7, 8), remaining_tasks=1, checkpoint_pause=False, checkpoint_phase=0, testing="")
    of = lambda started: FeatureData({"tasks": tasks, "plans": PlansData((), started, 0)})
    following = FollowingPlan(plan_id=5, task_id=7, approved=True, logged_at=10.0)
    assert following.on_push(auto) == () and isinstance(FollowingPlan(plan_id=5).on_push(auto), Block), "an unapproved plan is refused"
    closed = following.respond(TaskClosed(environment_id=1, time=20.0, task_id=7, outcome="completed").with_data(of(plan)), auto)
    assert closed.target == replace(following, task_id=0, origin_state=7) and not closed.popped
    assert following.respond(TaskClosed(environment_id=1, time=20.0, task_id=9, outcome="completed").with_data(of(plan)), auto).target == following
    started = closed.target.respond(TaskStarted(environment_id=1, time=30.0, task_id=8, title="next", plan_id=5).with_data(of(replace(plan, started_task=8))), auto)
    assert started.target == replace(following, task_id=8, origin_state=7, logged_at=30.0)
    checkpoint_pause = following.respond(TaskClosed(environment_id=1, time=20.0, task_id=7, outcome="completed").with_data(of(replace(plan, checkpoint_pause=True, checkpoint_phase=2))), auto)
    assert checkpoint_pause.target == replace(following, task_id=0, origin_state=7, checkpoint_pause=True, phase=2)
    stopped = checkpoint_pause.target.respond(Stop().with_data(of(plan)), auto)
    assert stopped.refusal.rendered().startswith("plan 5: phase 2 is complete")
    waits = checkpoint_pause.target.respond(Stop().with_data(of(plan)), manual)
    assert waits.refusal is None and waits.nudges[0].rendered().startswith("plan 5: phase 2 is complete, a checkpoint")
    assert checkpoint_pause.target.respond(SessionStarted(time=40.0).with_data(of(plan)), auto).nudges[0].key == "plans.phase_complete_at_a_checkpoint"
    assert checkpoint_pause.target.respond(ToolStarting(call=ToolCall(tool="Edit", input={}, operation=Claude().operation("Edit", {}), writes=True), time=41.0).with_data(of(plan)), auto).target == checkpoint_pause.target, "counts nothing at a checkpoint"
    finished = following.respond(PlanFinished(environment_id=1, time=50.0, plan_id=5).with_data(of(None)), auto)
    assert finished.popped and [n.key for n in finished.nudges] == ["plans.plan_done"]
    assert not following.respond(PlanFinished(environment_id=1, time=50.0, plan_id=6).with_data(of(plan)), auto).popped
    pushed = PlansReady().respond(PlanStarted(environment_id=1, time=1.0, plan_id=5, task_id=7).with_data(of(plan)), auto)
    assert pushed.pushed == FollowingPlan(plan_id=5, task_id=7, approved=True, logged_at=1.0)
    owned = PlansReady().respond(TaskStarted(environment_id=1, time=2.0, task_id=3, title="t", plan_id=0).with_data(of(None)), auto)
    assert owned.pushed == PlansWorking(task_id=3, logged_at=2.0)
    planned = PlansReady().respond(TaskStarted(environment_id=1, time=2.0, task_id=7, title="t", plan_id=0).with_data(of(plan)), auto)
    assert planned.pushed == FollowingPlan(plan_id=5, task_id=7, approved=True, logged_at=2.0)
    became = PlansWorking(task_id=7, logged_at=1.0, edits=2).respond(PlanStarted(environment_id=1, time=3.0, plan_id=5, task_id=7).with_data(of(plan)), auto)
    assert became.target == FollowingPlan(plan_id=5, task_id=7, approved=True, logged_at=1.0, edits=2)


def test_following_plan_pops_when_the_plan_is_postponed_or_abandoned_and_on_resume_when_it_is_no_longer_started():
    from dataclasses import replace
    from journal.features.plans.states.following_plan import FollowingPlan
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.plans.support.started_plan import StartedPlan
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.events.rows.plan_abandoned import PlanAbandoned
    from journal.events.rows.plan_postponed import PlanPostponed
    settings = SettingsValue({})
    tasks = TasksData(current_task=7, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=())
    plan = StartedPlan(plan_id=5, next_task=8, started_task=7, started_task_briefing="", recent_tasks=(7, 8), remaining_tasks=2, checkpoint_pause=False, checkpoint_phase=0, testing="")
    of = lambda started: FeatureData({"tasks": tasks, "plans": PlansData((), started, 0)})
    following = FollowingPlan(plan_id=5, task_id=7, approved=True, logged_at=10.0)
    user_origin = following.respond(PlanPostponed(environment_id=1, time=20.0, plan_id=5, user_origin=True).with_data(of(None)), settings)
    assert user_origin.popped and [n.rendered() for n in user_origin.nudges] == ["the user postponed plan 5"]
    agent_index = following.respond(PlanPostponed(environment_id=1, time=20.0, plan_id=5, user_origin=False).with_data(of(None)), settings)
    assert agent_index.popped and agent_index.nudges == (), "the agent's own command needs no line"
    assert not following.respond(PlanPostponed(environment_id=1, time=20.0, plan_id=6, user_origin=True).with_data(of(plan)), settings).popped
    abandoned = following.respond(PlanAbandoned(environment_id=1, time=20.0, plan_id=5, user_origin=True).with_data(of(None)), settings)
    assert abandoned.popped and [n.rendered() for n in abandoned.nudges] == ["the user abandoned plan 5"]
    assert following.on_resume(of(None), settings).popped, "beneath a wait, a plan postponed meanwhile is over on resume"
    assert following.on_resume(of(replace(plan, plan_id=6)), settings).popped, "another plan started meanwhile: this one is over"
    assert following.on_resume(of(plan), settings) == (), "still the plan started here: the work goes on in silence"


def test_a_question_asked_pushes_waiting_and_its_answer_pops_it_on_top_or_on_resume():
    from journal.engine.states.compacting import Compacting
    from journal.features.questions.states.waiting import Waiting
    from journal.features.questions.questions_conduct import QuestionsConduct
    from journal.features.questions.support.questions_data import QuestionsData
    from journal.events.rows.question_answered import QuestionAnswered
    from journal.events.rows.question_posed import QuestionPosed
    from journal.events.agent.stop import Stop
    settings = SettingsValue({})
    of = lambda *open: FeatureData({"questions": QuestionsData(open=open)})
    requested = Working(task_id=7, logged_at=1.0).respond(QuestionPosed(environment_id=1, time=2.0, question_id=4).with_data(of(4)), settings, (QuestionsConduct,))
    assert requested.pushed == Waiting(question_id=4), "a question asked pushes the wait on the work in hand"
    waiting = Waiting(question_id=4)
    answered = waiting.respond(QuestionAnswered(environment_id=1, time=3.0, question_id=4).with_data(of()), settings, (QuestionsConduct,))
    assert answered.popped and [n.rendered() for n in answered.nudges][0].startswith("question 4 is answered")
    assert not waiting.respond(QuestionAnswered(environment_id=1, time=3.0, question_id=5).with_data(of(4)), settings, (QuestionsConduct,)).popped, "another question's answer is not this one's"
    assert waiting.respond(SessionStarted(time=4.0).with_data(of(4)), settings, (QuestionsConduct,)).popped is False and waiting.respond(Stop().with_data(of(4)), settings, (QuestionsConduct,)).refusal is None, "a stop while waiting is fine"
    assert waiting.on_resume(of(4), settings) == (), "beneath a compaction the wait stands while the question is open"
    assert waiting.on_resume(of(), settings).popped, "answered meanwhile, it pops on resume with the line"
    assert not Compacting().respond(QuestionAnswered(environment_id=1, time=3.0, question_id=4).with_data(of()), settings, (QuestionsConduct,)).popped, "the answer under a compaction waits for the resume"


def test_a_declared_wait_pushes_expecting_which_asks_on_the_ticks_and_pops_when_the_last_row_settles_and_stuck_is_quiet():
    from dataclasses import replace
    from journal.features.tasks.states.external_wait import ExternalWait
    from journal.features.tasks.states.impasse import Impasse
    from journal.models.open_task import OpenTask
    from journal.features.tasks.tasks_conduct import TasksConduct
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.events.agent.wait_request import WaitRequest
    from journal.events.agent.stop import Stop
    from journal.events.agent.impasse_report import ImpasseReport
    from journal.events.agent.ticked import Ticked
    from journal.events.rows.row_resolved import RowResolved
    auto, manual = SettingsValue({TasksOptions.AUTO.key: True, TasksOptions.SHORT_WAIT_SECONDS.key: 20}), SettingsValue({TasksOptions.AUTO.key: False, TasksOptions.SHORT_WAIT_SECONDS.key: 20})
    tasks = TasksData(current_task=7, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=OpenTask(9, "the next one", "", 0), last_commands=())
    of = lambda: FeatureData({"tasks": tasks})
    pushed = Working(task_id=7).respond(WaitRequest(focus="the build", end_refs="command_outputs:4,checks:2", time=100.0), auto, (TasksConduct,))
    assert pushed.pushed == ExternalWait.opened("the build", "command_outputs:4,checks:2", 100.0), "journal await pushes the wait on the work"
    assert Working(task_id=7).respond(ImpasseReport(reason="the login", time=1.0), auto, (TasksConduct,)).pushed == Impasse(reason="the login"), "journal stuck pushes Stuck"
    waiting = pushed.pushed
    held = waiting.respond(Stop(time=130.0).with_data(of()), auto).refusal
    assert held is not None and held.rendered().startswith("the build still runs, for a time the journal cannot estimate yet, and task 9 is open") and "carry on with task 9" in held.rendered(), "in auto mode a stop while a task is open is refused during a wait as without one"
    assert waiting.respond(Stop(time=130.0).with_data(of()), manual).refusal is None and waiting.respond(Ticked(silence_seconds=10.0, time=130.0).with_data(of()), auto).nudges == (), "out of auto mode a stop is fine, and an early tick is quiet"
    meanwhile = waiting.respond(Ticked(silence_seconds=70.0, time=170.0).with_data(of()), auto)
    assert meanwhile.target == replace(waiting, next_task_reported=True) and meanwhile.nudges[0].rendered().startswith("while you wait for the build, task 9 is next"), "in auto mode the next task is named once after a minute"
    assert waiting.respond(Ticked(silence_seconds=70.0, time=170.0).with_data(of()), manual).nudges == (), "out of auto mode it is not"
    from journal.features.tasks.support.wait_progress import WaitProgress
    estimated = lambda progress: FeatureData({"tasks": replace(tasks, wait_progress=progress)})
    slow = waiting.respond(Ticked(silence_seconds=1.0, time=101.0).with_data(estimated({"command_outputs:4": WaitProgress(100.0, 0.01)})), manual)
    assert slow.popped and slow.nudges[0].rendered().startswith("the build has about 99 seconds left, too long to wait") and "park it and carry on with task 9" in slow.nudges[0].rendered(), "a run at 1% a second is parked, naming the seconds left"
    quick = waiting.respond(Ticked(silence_seconds=1.0, time=109.0).with_data(estimated({"command_outputs:4": WaitProgress(100.0, 0.9)})), manual)
    assert not quick.popped and quick.target == replace(waiting, decided=True) and quick.nudges[0].rendered().startswith("the build has about 1 seconds left"), "a run at 90% is waited out"
    step = waiting.respond(Ticked(silence_seconds=1.0, time=110.0).with_data(estimated({"command_outputs:4": WaitProgress(100.0, 1 / 5)})), manual)
    assert step.popped, "a merge in step 1 of 5 is parked"
    assert waiting.respond(Stop(time=109.0).with_data(estimated({"command_outputs:4": WaitProgress(100.0, 0.9), "checks:2": WaitProgress(100.0, 0.9)})), auto).refusal is None, "a wait estimated short lets the stop through"
    from journal.features.tasks.support.wait_progress_reader import WaitProgressReader
    assert WaitProgressReader.finished_share(["step 1/5: asking the plugins"]) == 0.0 and WaitProgressReader.finished_share(["running tests [ 50%] 3 of 6 finished"]) == 0.5, "a step begun counts the steps before it as done, a count its finished share"
    assert WaitProgress(100.0, 0.5, last_seconds=300.0).remaining_seconds(160.0) == 240.0 and WaitProgress(100.0, 0.5, last_seconds=30.0).remaining_seconds(160.0) == 60.0, "the last passing run of the same command gives the estimate while the run is within it, then its progress"
    from journal.events.agent.tool_starting import ToolStarting
    conducted = SettingsValue({TasksOptions.AUTO.key: True, TasksOptions.SHORT_WAIT_SECONDS.key: 20, TasksOptions.PRIORITY_REMIND_TASKS.key: 99})
    awaiting = lambda line, progress: waiting.respond(ToolStarting(call=shell(line), time=105.0).with_data(estimated(progress)), conducted, (TasksConduct,)).refusal
    refused = awaiting("journal await 'the merge of worker 3' --output 4", {"command_outputs:4": WaitProgress(100.0, 0.0)})
    assert refused is not None and refused.rendered().startswith("the merge of worker 3 runs for a time the journal cannot estimate yet, too long to wait for while task 9 is open"), "an await on a process that does not end soon is refused while a task is open"
    assert awaiting("journal await 'the merge of worker 3' --output 4", {"command_outputs:4": WaitProgress(100.0, 0.0, last_seconds=10.0)}) is None, "one that ends within the setting's seconds may be awaited"
    assert waiting.respond(ToolStarting(call=shell("journal await 'the merge of worker 3' --output 4"), time=105.0).with_data(FeatureData({"tasks": replace(tasks, next_open=None)})), conducted, (TasksConduct,)).refusal is None, "with no task open a long process may be awaited"
    looked = meanwhile.target.respond(Ticked(silence_seconds=310.0, time=410.0).with_data(of()), auto)
    assert looked.target == replace(meanwhile.target, check_reminder=meanwhile.target.check_reminder.started(410.0)) and looked.nudges[0].rendered().startswith("you have waited 5 min on the build: check it"), "every five quiet minutes the agent is asked to look"
    assert looked.target.respond(Ticked(silence_seconds=400.0, time=500.0).with_data(of()), auto).nudges == (), "and not again before five more"
    first = waiting.respond(RowResolved(environment_id=1, time=200.0, ref="command_outputs:4", outcome="output 4 finished"), auto)
    assert first.target == replace(waiting, end_refs="checks:2", outcomes="output 4 finished") and not first.popped, "one row settled, one still to come"
    assert waiting.respond(RowResolved(environment_id=1, time=200.0, ref="tasks:3"), auto).target == waiting, "a row it does not wait on is not its business"
    last = first.target.respond(RowResolved(environment_id=1, time=300.0, ref="checks:2", outcome="check 2 passed"), auto)
    assert last.popped and last.nudges[0].rendered().startswith("wait over: output 4 finished; check 2 passed"), "the last row settled pops the wait with what each came to"
    assert Impasse(reason="the login").respond(Stop(time=1.0).with_data(of()), auto).refusal is None and Impasse(reason="the login").respond(Ticked(silence_seconds=900.0, time=901.0).with_data(of()), auto).nudges == (), "stuck is quiet"
    assert Impasse(reason="the login").respond(ToolStarting(call=ToolCall(tool="Read", input={}, operation=Claude().operation("Read", {}))), auto).popped, "its own tool use pops it"


def test_a_journal_command_is_no_tool_use_to_a_wait():
    from journal.features.questions.states.waiting import Waiting
    settings = SettingsValue({})
    waiting = Waiting(question_id=4)
    assert waiting.respond(ToolStarting(call=shell("journal task list")), settings).popped is False, "a journal command lifts no wait"
    assert waiting.respond(ToolStarting(call=shell("ls src")), settings).popped, "the agent's own tool use does"


def test_a_part_knows_whether_it_reads_an_output_and_the_shape_of_that_read():
    parts = shell("journal output read 12 --grep FAILED && ls src").parts
    assert (parts[0].reads_output, parts[0].read_shape) == (True, "journal output read <output> --grep FAILED"), "the number taken out, the read keeps its shape"
    assert not parts[1].reads_output and parts[1].read_shape == "ls src", "a part that reads no output has its own text as its shape"
    assert not shell("journal output read 3").parts[0].reads_output, "a plain read of a summary is no read by hand"


def test_the_engine_indexes_its_listeners_once_at_boot_and_the_container_builds_one_instance_per_class(app: App):
    from journal.events.agent.stop import Stop
    from journal.features.messages.messages_conduct import MessagesConduct
    from journal.repositories.agents import Agents
    from journal.support.agent_role import AgentRole
    machine = app.container.get(StateMachine)
    index, conducts = machine.listener_index, machine.features.conducts(AgentRole.MAIN)
    state = next(iter(machine.states.classes()))
    assert index.state_listeners(state, conducts, ToolStarting) == state.event_listeners(ToolStarting, conducts), "the boot's index holds what a registered state's listeners for an event are, worked out once"
    assert index.state_listeners(state, conducts, Stop) is index.state_listeners(state, conducts, Stop), "and hands the same answer every time"
    assert Working.event_listeners(ToolStarting, (MessagesConduct,)) != Working.event_listeners(ToolStarting), "the conducts a state hears are part of what its listeners are"
    assert app.container.get(StateMachine) is app.container.get(StateMachine) and app.container.get(Agents) is app.container.get(Agents), "the container builds a class once"


def test_a_listener_may_stop_an_events_propagation_and_the_compacting_state_switches_the_typist_off_until_it_pops_and_starts_the_tool_count_again(app: App, monkeypatch):
    from journal.events.agent.ticked import Ticked
    from journal.events.rows.message_arrived import MessageArrived
    from journal.supervisor_link import SupervisorLink

    class Talkative(Conduct):
        def on_ticked(self, event: Ticked, settings: SettingsValue) -> Transition:
            return self.none(LINE)

        def on_message_arrived(self, event: MessageArrived, settings: SettingsValue) -> Transition:
            return self.none(OTHER)

    @dataclass(frozen=True)
    class Plain(BaseState):
        name = "plain"

    @dataclass(frozen=True)
    class Stopping(BaseState):
        name = "stopping"

        def on_ticked(self, event: Ticked, settings: SettingsValue) -> Transition:
            event.stop_propagation()
            return self.none()

    settings = SettingsValue({})
    tick = Ticked(silence_seconds=1.0).with_data(FeatureData({}))
    arrived = MessageArrived(environment_id=1, time=2.0, text="hi").with_data(FeatureData({}))
    assert Plain().respond(tick, settings, (Talkative,)).nudges == (LINE,) and Plain().respond(arrived, settings, (Talkative,)).nudges == (OTHER,), "in any other state the conduct speaks"
    assert Stopping().respond(tick, settings, (Talkative,)).nudges == (), "a listener that stops the event's propagation is the last to hear it, so the conduct is silent"
    assert Plain().respond(tick, settings, (Talkative,)).nudges == (LINE,), "the next walk of the same event starts again"
    assert CompactingState().respond(arrived, settings, (Talkative,)).nudges == (OTHER,), "compacting stops nothing itself: what the conduct says queues at the typist"
    assert CompactingState().respond(ToolStarting(call=shell("ls")).with_data(FeatureData({})), settings, (Talkative,)).handed_down, "a tool call ends the compaction and goes to the state beneath"
    assert CompactingState().respond(SessionStarted(source="compact").with_data(FeatureData({})), settings, (Talkative,)).popped, "and the session's start still pops it"
    transmitted = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: transmitted.append(fields["line"]))
    hook(app, "SessionStart")
    write(app)
    write(app)
    agents, link = app.container.get(Agents), app.container.get(SupervisorLink)
    assert agents.session_agent("s1").tool_uses == 2
    link.resting(1)
    link.type(1, "first")
    link.type(1, "held behind the first")
    assert transmitted == ["[journal] first"] and len(link.typed._held) == 1, "a line behind one not yet seen back queues"
    assert hook(app, "PreCompact")[0] == 200
    assert agents.session_agent("s1").stack[-1]["state"] == "compacting" and agents.session_agent("s1").tool_uses == 0, "the compaction pushes its state and sets the count back to zero"
    link.type(1, "a dump arrived")
    link.type(1, "the wait ended")
    link.release(1)
    assert transmitted == ["[journal] first"] and link.typed.batched(1) is None, "the typist is disabled while compacting: its queue is emptied and a line is dropped, not queued, since the look after the compaction tells the agent what it missed"
    hook(app, "SessionStart", source="compact")
    assert agents.session_agent("s1").stack[-1]["state"] != "compacting" and transmitted == ["[journal] first"]
    link.typed.typed(1, "")
    link.typed._sent_at[1] = 0.0
    link.typed._waiting.clear()
    link.type(1, "a wait ended")
    assert transmitted == ["[journal] first", "[journal] a wait ended"], "and enabled again once the state left"


def test_a_task_started_outside_the_plan_is_the_task_in_hand_of_the_plan_state_and_its_nudges_name_it():
    from journal.features.plans.states.following_plan import FollowingPlan
    from journal.features.tasks.support.tasks_data import TasksData
    settings = SettingsValue({})
    following = FollowingPlan(plan_id=19, approved=True)
    assert following.label() == "plan 19, with no task in hand"
    held = TasksData(current_task=1141, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=(), agent_tasks=(1141,))
    started = following.respond(TaskStarted(environment_id=1, time=5.0, task_id=1141, title="the developer tab", plan_id=0).with_data(FeatureData({"tasks": held})), settings)
    assert started.target.task_id == 1141 and started.target.label() == "task 1141" and started.target.logged_at == 5.0, "one task is in hand at a time, so the task started is the plan state's task whether the plan holds it or not"


def test_the_work_mode_is_the_bottom_state_the_orchestrator_dispatches_the_builder_carries_on_and_the_solo_mode_keeps_workers_out():
    from journal.events.agent.stop import Stop
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.plans.support.started_plan import StartedPlan
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.features.workers.feature import Workers
    from journal.features.workers.states.delegating import Delegating
    from journal.features.workers.states.orchestrating import Orchestrating
    from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
    from journal.features.workers.states.soloing import Soloing
    from journal.models.open_task import OpenTask
    settings = lambda mode: SettingsValue({WorkersOptions.MODE.key: mode, TasksOptions.AUTO.key: True, TasksOptions.LOG_AGE_LIMIT.key: 10, TasksOptions.FIRST_DELAY.key: 25})
    tasks = TasksData(current_task=0, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=OpenTask(3, "the footer", "", 0), last_commands=(), agent_tasks=(7,), open_ids=(3, 4), open_count=2, open_next="task 3 (the footer), task 4 (the margin)")
    started = StartedPlan(plan_id=2, next_task=3, started_task=0, started_task_briefing="", recent_tasks=(3, 4), remaining_tasks=2, checkpoint_pause=False, checkpoint_phase=0, testing="")
    of = lambda plan: FeatureData({"plans": PlansData((), plan, 0), "tasks": tasks})
    from journal.engine.states_catalogue import StatesCatalogue
    from journal.engine.support.stack import Stack
    from journal.features.plans.states.plans_ready import PlansReady
    from journal.features.plans.states.plans_working import PlansWorking

    class ModeRegistry:
        def states(self):
            return [Ready, PlansReady, Orchestrating, Soloing]

        def modes(self):
            return [Workers.modes]

        def floors(self):
            return {}

    catalogue = StatesCatalogue(ModeRegistry())
    assert isinstance(catalogue.apply_mode(Stack((PlansReady(),)), settings("orchestrator")).states[0], Orchestrating), "the work mode's state is the bottom of every stack"
    from journal.engine.states.void import Void
    from journal.support.agent_role import AgentRole
    from journal.features.workers.states.working_task import WorkingTask
    worker_stacks = [catalogue.floor(Stack(layers), settings("orchestrator"), AgentRole.WORKER).states for layers in ((Orchestrating(), WorkingTask(task_id=4)), (WorkingTask(task_id=4),), (Void(),))]
    assert [[type(layer) for layer in layers] for layers in worker_stacks] == [[Void, WorkingTask], [Void, WorkingTask], [Void]], "a helper's stack rests on Void, never on the main agent's mode, and keeps its work above it"
    planned = Orchestrating().respond(SessionStarted(time=1.0).with_data(of(started)), settings("orchestrator"))
    assert isinstance(planned.pushed, OrchestratingPlan) and planned.pushed.plan_id == 2, "a started plan is pushed over the mode state as the orchestrator's plan state"
    assert type(catalogue.apply_mode(Stack((Orchestrating(),)), settings("builder")).states[0]) is PlansReady, "the builder's mode state is Idle with plans"
    stop = Orchestrating().respond(Stop().with_data(of(None)), settings("orchestrator"))
    assert stop.refusal is not None and "task 3 (the footer), task 4 (the margin)" in stop.refusal.rendered() and "dispatch a worker" in stop.refusal.rendered(), "the orchestrator's stop is held with the tasks to dispatch"
    from dataclasses import replace as replaced
    all_blocked = FeatureData({"plans": PlansData((), None, 0), "tasks": replaced(tasks, open_ids=(), open_next="", blocked=(5, 8))})
    held = Orchestrating().respond(Stop().with_data(all_blocked), settings("orchestrator"))
    told = held.refusal.rendered()
    assert "tasks 5, 8" in told and "truly blocked" in told and "report what you decided" in told and "journal stuck" in told, "an orchestrator whose every task is blocked may not stop: it checks them, decides what it can, waits on its workers or says it is stuck"
    some_blocked = FeatureData({"plans": PlansData((), None, 0), "tasks": replaced(tasks, blocked=(5,))})
    busy = Orchestrating().respond(Stop().with_data(some_blocked), settings("orchestrator"))
    assert busy.refusal.rendered().startswith("tasks 5 are blocked"), "a stop round asks about the blocked tasks before the open ones"
    again = busy.target.respond(Stop().with_data(some_blocked), settings("orchestrator"))
    assert "dispatch a worker" in again.refusal.rendered(), "and then holds the stop with the tasks to dispatch"
    assert WorkersNudges.BLOCKED_CHECK.repeat == Timeout.seconds(300), "and the check comes again every five minutes while it holds"
    assert "task 3" in PlansReady().respond(Stop().with_data(of(None)), settings("builder")).refusal.rendered() and "dispatch" not in PlansReady().respond(Stop().with_data(of(None)), settings("builder")).refusal.rendered(), "the builder's stop names the next task to do"
    assert isinstance(Orchestrating().respond(TaskStarted(environment_id=1, time=2.0, task_id=7, title="x", plan_id=0).with_data(of(None)), settings("orchestrator")).pushed, Delegating), "a task started in the orchestrator's mode is delegating, not working"
    delegating = Delegating(task_id=7, logged_at=1.0).respond(Stop(time=2.0).with_data(of(None)), settings("orchestrator"))
    assert delegating.refusal is not None and "hand it to a worker" in delegating.refusal.rendered(), "the delegating task says hand it over where working says carry on"
    assert isinstance(catalogue.apply_mode(Stack((PlansReady(), PlansWorking(task_id=1))), settings("solo")).states[0], Soloing), "a mode changed while work is in hand changes the bottom beneath it"
    assert Soloing().respond(ToolStarting(call=shell("journal worker dispatch 'Mr. Smith' 'the job' --profile journal-medior")).with_data(of(None)), settings("solo")).refusal == WorkersNudges.SOLO_DISPATCH.create(), "solo keeps workers out"
    assert Soloing().respond(ToolStarting(call=shell("ls")).with_data(of(None)), settings("solo")).refusal is None


def test_an_orchestrator_driven_through_a_plan_of_twenty_tasks_with_workers_never_stalls(app: App, monkeypatch):
    import subprocess
    import time as timing
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.supervisor_link import SupervisorLink
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: None)
    working = []

    def started(runner, worker, actor):
        working.append(subprocess.Popen(["sleep", "60"], start_new_session=True))
        runner.workers.save(worker.running_as(working[-1].pid, timing.time()), actor)

    monkeypatch.setattr(WorkerRunner, "start", started)
    try:
        orchestrated(app)
    finally:
        for process in working:
            process.kill()
            process.wait()


def orchestrated(app: App) -> None:
    """Twenty tasks through the orchestrator, each dispatched worker standing in as a process that runs until the test lets it go."""
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.repositories.workers import Workers as WorkerRows
    app.container.get(SettingRows).set("workers.mode", "orchestrator", Actor.user(1))
    hook(app, "SessionStart")
    console, agents, tasks = app.console(), app.container.get(Agents), app.container.get(Tasks)
    console.run(["environment", "overview"], AGENT)
    console.run(["plan", "create", "go live", "--brief", "twenty tasks"], USER)
    console.run(["plan", "phase", "1", "release", "--when", "all twenty done"], USER)
    for n in range(1, 21):
        console.run(["plan", "add", "1", f"piece {n}", "--brief", f"piece {n} is done"], USER)
    console.run(["plan", "todos", "1", "1", *[str(n) for n in range(1, 21)]], USER)
    assert console.run(["plan", "ready", "1"], AGENT).code == 0 and console.run(["plan", "approve", "1"], USER).code == 0 and console.run(["plan", "start", "1"], AGENT).code == 0
    stack = lambda: [s["state"] for s in agents.session_agent("s1").stack]
    assert stack() == ["orchestrating", "orchestrating_plan"] and tasks.find(1).state == "open", "the orchestrator's mode state and its plan state, every piece left open for workers"
    stop = lambda active=False: hook(app, "Stop", stop_hook_active=active)[1]
    first = stop()
    assert first.get("decision") == "block" and "20 tasks are open" in first["reason"] and "dispatch a worker" in first["reason"] and "is in hand" not in first["reason"], "a stop is refused with the open pieces to dispatch"
    for n, name in ((1, "Ada"), (2, "Florence"), (3, "Babbage")):
        assert console.run(["worker", "dispatch", name, f"do piece {n}", "--changes", "the files of its task", "--tests", "Scoped tests", "--profile", "journal-medior", "--model", "sonnet", "--task", str(n)], AGENT).code == 0, "a worker is put on an open piece of the plan"
    waiting = stop()
    assert stack()[-1] == "awaiting" and "journal worker wait" not in waiting.get("reason", ""), "waiting on the workers it dispatched, a stop goes through"
    workers = app.container.get(WorkerRows)
    for n in (1, 2, 3):
        app.container.get(WorkerRunner).run(workers.find(n), ["sh", "-c", "echo the piece is done"], Actor.agent("s1"))
    assert stack() == ["orchestrating", "orchestrating_plan"], "the last report pops the wait and the orchestrator is back on its plan"
    for n in (1, 2, 3):
        assert console.run(["worker", "complete", str(n)], AGENT).code == 0
        assert console.run(["task", "complete", str(n), "--how", "reviewed and merged"], AGENT).code == 0
    app.runtime().deferred.drain()
    assert tasks.find(4).state == "open" and stack()[-1] == "orchestrating_plan", "the plan leaves its next open piece for a worker"
    for n in range(4, 21):
        assert stop().get("decision") == "block", f"a stop with piece {n} and the rest open is refused, never allowed"
        assert console.run(["task", "start", str(n)], AGENT).code == 0
        hook(app, "PreToolUse", tool_name="Bash", tool_input={"command": f"journal task complete {n} --how done"})
        assert console.run(["task", "complete", str(n), "--how", "done"], AGENT).code == 0
        app.runtime().deferred.drain()
    assert app.container.get(Plans).find(1).state == "done" and stack() == ["orchestrating"], "the plan is done and the orchestrator is back in its mode state"
    assert stop().get("decision") != "block", "with nothing open the stop passes"


def test_a_stop_with_the_tasks_log_older_than_the_set_minutes_asks_for_the_log_line_first():
    from journal.events.agent.stop import Stop
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.tasks.support.tasks_data import TasksData
    data = FeatureData({"plans": PlansData((), None, 0), "tasks": TasksData(current_task=7, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=())})
    settings = lambda minutes: SettingsValue({TasksOptions.AUTO.key: True, TasksOptions.LOG_AGE_LIMIT.key: minutes, TasksOptions.FIRST_DELAY.key: 25, WorkersOptions.MODE.key: "builder"})
    working = Working(task_id=7, logged_at=0.0)
    assert working.respond(Stop(time=5 * 60.0).with_data(data), settings(10)).refusal.key == "tasks.carry_on", "within the minutes a stop is told to carry on"
    assert working.respond(Stop(time=11 * 60.0).with_data(data), settings(10)).refusal.key == "tasks.log_first_at_stop", "past them the log line comes first"
    assert working.respond(Stop(time=2 * 60.0).with_data(data), settings(1)).refusal.key == "tasks.log_first_at_stop", "the minutes are the user's to set"


def test_a_long_journal_line_reaches_the_agent_whole_in_several_marked_pieces(app: App, monkeypatch):
    from journal.supervisor_link import SupervisorLink
    transmitted = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: transmitted.append(fields["line"]))
    from journal.support.typed_lines import TypedLines
    app.container.get(SettingRows).set("delivery.batch_seconds", 0, Actor.user(1))
    terms = " ".join(f"word{n}" for n in range(1, 260))
    link, lines = app.container.get(SupervisorLink), app.container.get(TypedLines)
    link.type(1, terms)
    assert len(transmitted) == 1, "one segment at a time goes into the box"
    while lines.confirm(1, transmitted[-1]):
        link.release(1)
    assert len(transmitted) >= 3 and all(len(segment) <= 600 and segment.startswith("[journal] ") for segment in transmitted), "typed in whole pieces a terminal takes, each the journal's"
    assert " ".join(segment.removeprefix("[journal] ") for segment in transmitted) == terms and "..." not in " ".join(transmitted), "nothing cut short"


def test_every_listener_of_a_state_or_a_conduct_is_named_on_and_its_event():
    import importlib
    import pkgutil
    import re
    import journal
    from typing import get_type_hints
    for module in pkgutil.walk_packages(journal.__path__, "journal."):
        importlib.import_module(module.name)
    snake = lambda name: re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def lineage(cls: type) -> set[type]:
        return {cls, *(member for child in cls.__subclasses__() for member in lineage(child))}

    owners = lineage(Conduct) | lineage(BaseState)
    misnamed = [f"{owner.__name__}.{name}" for owner in owners for name, method in vars(owner).items()
                if name.startswith("on_") and callable(method) and "event" in get_type_hints(method) and name != f"on_{snake(get_type_hints(method)['event'].__name__)}"]
    assert misnamed == [], "a listener is on_ and its event's name in snake case"


def test_a_workers_turns_and_its_brief_are_messages_of_its_own_chat_with_their_tags_left_as_text(app: App, tmp_path, monkeypatch):
    """What a worker writes, read from its transcript after its hooks are answered and again at its run's end, becomes its messages once each, in a worker's chat, its tags plain text; the job it was given is the first message to it."""
    from journal.support.agent_role import AgentRole
    from journal.models.worker import Worker
    from journal.providers.claude import Claude
    from journal.repositories.messages import Messages
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.features.workers.support.worker_chat import WorkerChat
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.support.agent_token import AgentToken
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    transcript = home / ".claude" / "projects" / Claude.folder_name(app.config.root) / "w1.jsonl"
    transcript.parent.mkdir(parents=True)
    said = lambda text: json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}) + "\n"
    transcript.write_text(said("[!reply:1] the parser reads") + said("[!todo=\"a stray task\"] names next"))
    hook(app, "SessionStart")
    app.console().run(["message", "send", "how is the parser?"], USER)
    app.console().run(["message", "read", "1"], AGENT)
    scope, workers, messages = app.container.get(Scope), app.container.get(Workers), app.container.get(Messages)
    with scope.environment(1):
        worker = workers.save(Worker(environment_id=1, name="Mr. Babbage", brief="b", session="w1", token_hash=AgentToken.hashed("tok")), Actor.system())
        workers.save(workers.find(worker.id).dispatched(1.0), Actor.agent("s1"))
    data = json.dumps({"hook_event_name": "PreToolUse", "session_id": "w1", "tool_name": "Bash", "tool_input": {"command": "journal clock-in"}}).encode()
    urlopen(HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=data, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main", "X-Journal-Actor": f"worker:{worker.id}", "X-Journal-Actor-Token": "tok"}), timeout=5).read()
    app.runtime().deferred.drain()
    chat = lambda: [(m.author, m.text) for m in messages.all() if m.agent_role == AgentRole.WORKER and m.session == "w1"]
    with scope.environment(1):
        assert chat() == [("user", "b"), ("agent", "[!reply:1] the parser reads"), ("agent", '[!todo="a stray task"] names next')], "the job, then each block the worker wrote, as its own messages"
        assert [m.id for m in messages.unanswered()] == [1] and not app.container.get(Tasks).all(), "its tags are text: they answer nothing and file nothing"
        transcript.write_text(transcript.read_text() + said("the parser is done"))
        app.container.get(WorkerRunner).finish(workers.find(worker.id), 0, Actor.system())
        app.container.get(WorkerChat).read(workers.find(worker.id))
        assert chat()[-1] == ("agent", "the parser is done") and len(chat()) == 4, "its last words are read at its run's end, and a second read writes nothing again"
        assert workers.find(worker.id).transcript_bytes == transcript.stat().st_size, "where the read stopped is kept on the worker's row, so a restart reads on from there"
        workers.save(workers.find(worker.id).notified("check the header too", 3.0, "agent:s1"), Actor.agent("s1"))
        transcript.write_text(transcript.read_text() + json.dumps({"type": "queue-operation", "operation": "enqueue", "content": "check the header too"}) + "\n")
        app.runtime().deferred.drain()
        app.container.get(WorkerChat).read(workers.find(worker.id))
        assert chat()[-1] == ("user", "check the header too") and len(chat()) == 5, "a note is written once, where it is sent, never again from the transcript"


def test_a_subagents_prompt_the_message_sent_to_it_and_its_turns_are_messages_of_its_own_chat(app: App, tmp_path, monkeypatch):
    """A subagent's prompt opens its chat once its transcript has words, each block it writes follows once, read after its hooks, and a message the agent sends it later is a message to it; none of it is in the main chat."""
    from journal.support.agent_role import AgentRole
    from journal.providers.claude import Claude
    from journal.repositories.messages import Messages
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    transcript = home / ".claude" / "projects" / Claude.folder_name(app.config.root) / "s1" / "subagents" / "agent-a9.jsonl"
    transcript.parent.mkdir(parents=True)
    said = lambda text: json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}) + "\n"
    hook(app, "SessionStart")
    agent = {"subagent_type": "journal-researcher", "description": "map the hooks", "prompt": "read the hooks", "model": "sonnet"}
    hook(app, "PreToolUse", tool_name="Agent", tool_input=agent, tool_use_id="t-1")
    hook(app, "PostToolUse", tool_name="Agent", tool_input=agent, tool_response={"isAsync": True, "agentId": "a9"}, tool_use_id="t-1")
    transcript.write_text(said("the hooks are in hooks/"))
    hook(app, "PostToolUse", tool_name="Read", tool_input={"file_path": "a.py"}, tool_response="", agent_id="a9")
    app.runtime().deferred.drain()
    hook(app, "PreToolUse", tool_name="SendMessage", tool_input={"to": "a9", "message": "and the receiver?"}, tool_use_id="t-2")
    app.runtime().deferred.drain()
    transcript.write_text(transcript.read_text() + said("the receiver is hooks/receiver.py"))
    hook(app, "SubagentStop", agent_id="a9")
    app.runtime().deferred.drain()
    messages = app.container.get(Messages)
    with app.container.get(Scope).environment(1):
        chat = [(m.author, m.text) for m in messages.all() if m.agent_role == AgentRole.SUBAGENT and m.session == "a9"]
        assert chat == [("user", "map the hooks read the hooks"), ("agent", "the hooks are in hooks/"), ("user", "and the receiver?"), ("agent", "the receiver is hooks/receiver.py")]
        assert not [m for m in messages.selected(messages.main_chat()) if m.session == "a9"], "none of it is in the main chat"


def test_the_log_reminder_comes_once_after_so_many_edits_or_minutes_since_the_last_log_whichever_is_first():
    from dataclasses import replace

    from journal.features.tasks.states.working import Working

    settings = SettingsValue({"tasks.first_nudge_after": 3, "tasks.log_old_after_minutes": 10, "tasks.log_after": 50, "tasks.name_every": 25})
    written = {"file_path": "a.py", "content": "x"}
    write = ToolStarting(call=ToolCall.decoded("Write", written, Claude().operation("Write", written), ()))
    read = ToolStarting(call=ToolCall.decoded("Read", {"file_path": "a.py"}, Claude().operation("Read", {"file_path": "a.py"}), ()))

    def at(event, time):
        return replace(event, time=time)

    def said(answer):
        return [n.name for n in answer.nudges]

    working, told = Working(task_id=1, logged_at=0.0), []
    for second in (1.0, 2.0, 3.0, 4.0):
        answer = working.respond(at(write, second), settings)
        working, told = answer.target or working, told + said(answer)
    assert told.count("log_where_it_stands") == 1, "after three edits with no log the log is asked for, and once"
    quiet = Working(task_id=1, logged_at=0.0, edits=1)
    assert said(quiet.respond(at(read, 300.0), settings)) == [], "five minutes and one edit: not yet"
    late = quiet.respond(at(read, 601.0), settings)
    assert said(late) == ["log_where_it_stands"], "ten minutes with few edits ask for it too, on any tool use"
    fresh = late.target.logged(602.0)
    assert said(fresh.respond(at(write, 603.0), settings)) == [] and not fresh.log_requested, "right after a log nothing is asked"
    assert fresh.respond(at(Stop(), 700.0), settings).refusal.name == "carry_on", "a stop inside the span carries on"
    assert late.target.respond(at(Stop(), 700.0), settings).refusal.name == "log_first_at_stop", "a stop past the span asks for the log first"


def test_claude_codes_switch_model_menu_is_recognised_in_a_narrow_terminal_and_a_model_picker_is_not():
    import textwrap
    from journal.providers.support.menu import Menu
    warning = "This conversation is cached for the current model. Switching to \x1b[1mOpus 5.5\x1b[22m means the full history gets re-read on your next message."
    wrapped = "\r\n".join(textwrap.wrap(warning, 40))
    frame = ("\x1b[38;5;209mBefuddling… (46s · ↓ 1.9k tokens · thinking with high effort)\x1b[0m\r\n\r\n" + "─" * 40 + "\r\n"
             "\x1b[1;33mSwitch model?\x1b[0m\r\nYour next response will be slower and\r\nuse more tokens\r\n\r\n" + wrapped + "\r\n\r\n"
             "\x1b[38;5;147m❯ 1. Yes, switch to Opus 5.5\x1b[0m\r\n  2. No, go back\r\n\r\n" + "─" * 40 + "\r\n\r\n" + "─" * 40 + "\r\n"
             "▸▸ bypass permissions on (shift+tab to cycle) · ← for agents\r\n")
    menu = Menu.parsed(frame)
    assert "Switch model?" not in menu.question, "the wrapped warning pushes the menu's title out of the lines read as its question"
    assert menu.switching_model() and menu.accepting().label == "Yes, switch to Opus 5.5", "the switch is still recognised, by its yes option, and that option is the one taken"
    picker = Menu.parsed("Select model\r\n❯ 1. Opus 5.5\r\n  2. Sonnet 5.5\r\n  3. Haiku 5.5\r\nEnter to confirm · Esc to exit\r\n")
    assert not picker.switching_model(), "a picker that names models but asks to switch nothing is not taken for the switch"


def test_a_codex_hook_review_menu_is_answered_by_trusting_the_hooks_the_journal_wrote(app: App, monkeypatch):
    import os
    import time as timing
    from journal.engine.menu_watcher import MenuWatcher
    from journal.repositories.messages import Messages
    from journal.supervisor_link import SupervisorLink
    transmitted = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: transmitted.append({"verb": verb, **fields}))
    hook(app, "SessionStart")
    watcher = app.container.get(MenuWatcher)
    agent = app.container.get(SessionAgents).agent("s1", 1)
    screens = app.config.home / "runtime" / "screens"
    screens.mkdir(parents=True, exist_ok=True)
    (app.config.home / "runtime" / "inboxes").mkdir(parents=True, exist_ok=True)
    (app.config.home / "runtime" / "inboxes" / "main").write_text(json.dumps({"socket": "/tmp/none.sock", "protocol": 1, "screen": str(screens / "main.out")}))
    screen = screens / "main.out"
    screen.write_text("  Hooks need review\r\n  9 hooks are new or changed in .codex/hooks.json\r\n\r\n› 1. Review hooks\r\n  2. Trust all and continue\r\n  3. Continue without trusting\r\n\r\n  Press enter to confirm or esc to go back\r\n")
    os.utime(screen, (timing.time() - 5, timing.time() - 5))
    keys = watcher.check(agent)
    assert keys == "\x1b[B\r" and transmitted[-1] == {"verb": "keys", "name": "agent", "keys": "\x1b[B\r"}, "the cursor goes down to option 2, Trust all and continue, and takes it"
    with app.container.get(Scope).environment(1):
        assert any('chose "Trust all and continue"' in m.text for m in app.container.get(Messages).scoped()), "and a card in the chat says so"


def test_an_agent_stopped_at_the_context_limit_has_compact_typed_once_and_an_ordinary_stop_or_a_mention_has_nothing(app: App, monkeypatch):
    from journal.features.usage.jobs.context_limit_compaction import ContextLimitCompaction
    from journal.supervisor_link import SupervisorLink
    transmitted = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: transmitted.append({"verb": verb, **fields}))
    hook(app, "SessionStart")
    job = app.container.get(ContextLimitCompaction)
    screens = app.config.home / "runtime" / "screens"
    screens.mkdir(parents=True, exist_ok=True)
    (app.config.home / "runtime" / "inboxes").mkdir(parents=True, exist_ok=True)
    (app.config.home / "runtime" / "inboxes" / "main").write_text(json.dumps({"socket": "/tmp/none.sock", "protocol": 1, "screen": str(screens / "main.out")}))
    prompt = "\r\n──────\r\n❯ \r\n──────\r\n  agent-journal · main\r\n"
    notice = "  ⎿  \x1b[31mContext\x1b[1Climit reached\x1b[39m · /compact or /clear to continue\r\n"
    limited = "> go on with the footer\r\n" + notice + prompt
    shown = lambda text: [(screens / "main.out").write_text(text), job.tick(0.0)]
    shown("⏺ Done, the footer is in.\r\n" + prompt)
    assert transmitted == [], "an ordinary stop has nothing typed"
    shown(notice + "".join(f"⏺ line {n} of the reply\r\n" for n in range(8)) + prompt)
    assert transmitted == [], "the notice higher on the screen, above the reply that came after it, is a mention"
    shown("⏺ The colleague's agent stopped with Context limit reached · /compact or /clear to continue\r\n" + prompt)
    assert transmitted == [], "words that merely quote the notice inside a line of the agent's are a mention"
    hook(app, "PreToolUse", tool_name="Read", tool_input={"file_path": "a.py"})
    shown(limited)
    assert transmitted == [], "the notice arriving while the agent uses tools, its turn not over, is a mention"
    hook(app, "UserPromptSubmit", prompt="go on with the footer")
    shown(limited)
    job.tick(0.0)
    assert transmitted == [{"verb": "type", "name": "agent", "line": "/compact", "after": 0.0}], "a prompt stopped at the context limit, which fires no stop hook, has /compact typed into the front, once while the notice stays"
    shown("✻ Compacting conversation… (4s)\r\n" + prompt)
    shown(limited)
    assert len(transmitted) == 2, "the next stop at the limit is a new occurrence and is compacted again"


def test_a_compaction_that_left_no_start_never_keeps_the_agents_lines_off_under_another_state():
    from journal.engine.states.compacting import Compacting
    from journal.events.agent.tool_finished import ToolFinished
    from journal.events.agent.turn_displayed import TurnDisplayed
    from journal.events.feature_data import FeatureData
    settings = SettingsValue({})
    read = ToolCall.decoded("Read", {"file_path": "a.py"}, Claude().operation("Read", {"file_path": "a.py"}), ())
    assert Compacting().respond(ToolFinished(call=read, output=""), settings).popped, "a tool finishing shows the compaction is over"
    assert Compacting().respond(TurnDisplayed(text="Done."), settings).popped, "and so do the agent's words shown"
    resumed = Compacting().on_resume(FeatureData({}), settings)
    assert resumed.popped, "a state pushed over it popping leaves it no longer compacting, so typing comes back"


def compaction_that_never_started(app: App, monkeypatch, between) -> list:
    from journal.supervisor_link import SupervisorLink
    transmitted = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: transmitted.append(fields["line"]))
    agents = app.container.get(Agents)
    hook(app, "SessionStart")
    app.console().run(["task", "create", "the footer", "--start"], AGENT)
    hook(app, "PreToolUse", tool_name="Bash", tool_input={"command": "journal await"})
    assert hook(app, "PreCompact", trigger="auto")[0] == 200 and agents.session_agent("s1").stack[-1]["state"] == "compacting", "Claude Code sends PreCompact in the middle of a tool call, and no compaction start follows"
    between()
    hook(app, "PostToolUse", tool_name="Bash", tool_input={"command": "journal await"}, tool_response={"stdout": ""})
    hook(app, "Stop")
    return transmitted


def user_message_lines(app: App, transmitted: list) -> list[str]:
    from journal.models.author import Author
    from journal.models.message import Message
    from journal.repositories.messages import Messages
    from journal.repositories.scope import Scope
    from journal.support.actor import Actor
    from journal.support.listener_queue import ListenerQueue
    from journal.supervisor_link import SupervisorLink
    app.container.get(SupervisorLink).resting(1)
    with app.container.get(Scope).environment(1):
        message = app.container.get(Messages).save(Message(author=Author.USER, text="hello?"), Actor.user(1))
    app.container.get(ListenerQueue).drain()
    return [line for line in transmitted if f"new message {message.id}" in line]


def test_a_message_reaches_a_stopped_agent_after_a_compaction_that_never_started(app: App, monkeypatch):
    transmitted = compaction_that_never_started(app, monkeypatch, lambda: None)
    assert app.container.get(Agents).session_agent("s1").stack[-1]["state"] != "compacting", "the tool's end shows no compaction is running"
    assert user_message_lines(app, transmitted), "so a message the user sends to the stopped agent is typed into its terminal at once"


def test_a_message_reaches_an_agent_waiting_on_top_of_a_compaction_that_never_started(app: App, monkeypatch):
    agents = app.container.get(Agents)
    transmitted = compaction_that_never_started(app, monkeypatch, lambda: app.console().run(["await", "the designs", "--until", "false"], AGENT))
    assert [s["state"] for s in agents.session_agent("s1").stack][-2:] == ["compacting", "awaiting"], "the await the tool ran pushed its wait over the compaction, so the tool's end and the stop went to the wait"
    assert user_message_lines(app, transmitted), "only the state on top decides whether lines are typed, so the waiting agent still gets the user's message at once"
    hook(app, "PreToolUse", tool_name="Read", tool_input={"file_path": "a.py"})
    assert "compacting" not in [s["state"] for s in agents.session_agent("s1").stack], "and once the wait pops, the compaction beneath it pops too"


def test_a_demand_never_counts_or_blocks_a_journal_command_whatever_its_feature_declares():
    from journal.engine.demand import Demand
    from journal.engine.demand_conduct import DemandConduct
    from journal.engine.demand_progress import DemandProgress
    from journal.engine.nudge import Nudge
    from journal.support.timeout import Timeout
    line = Nudge("test", "owed_line", "owed: {{left}}")
    strict = Demand(key="test.strict", requirement=lambda data: "owed", line=lambda requirement, balance: line.create(left=balance), refusal=lambda requirement: line.create(left=0), exemption=lambda event, requirement: False, span=lambda settings: Timeout.tool_uses(0), block_scope=lambda event: True)
    expired = DemandProgress(strict, "owed", Moment(tool_uses=0), Moment(tool_uses=5))
    data = FeatureData({"demands": (expired,)})
    settings = SettingsValue({})
    assert Ready().respond(ToolStarting(call=shell("journal task list")).with_data(data), settings, (DemandConduct,)).refusal is None, "a journal command passes a demand that exempts nothing"
    assert Ready().respond(ToolStarting(call=shell("ls")).with_data(data), settings, (DemandConduct,)).refusal is not None


def test_five_stops_held_in_a_row_let_the_next_through_in_a_state_that_asks_for_journal_panic_and_a_report(app: App, monkeypatch, tmp_path):
    hook(app, "SessionStart")
    held = [hook(app, "Stop")[1] for _ in range(5)]
    assert all(body.get("decision") == "block" for body in held), "the overview not read holds each stop"
    assert "journal panic report" in held[-1]["reason"], "the fifth held stop says the journal is likely stuck and how to get out"
    assert app.container.get(SessionAgents).top("s1").name == "panicking"
    assert hook(app, "Stop")[1].get("decision") != "block", "the sixth stop goes through"
    console = app.console()
    written = console.run(["panic", "report"], AGENT)
    report = int(re.search(r"report (\d+) written", written.text).group(1))
    body = app.container.get(Reports).find(report).body
    assert "environment overview" in body and "panicking" in body and "## Version" in body, body
    monkeypatch.setenv("PATH", str(tmp_path))
    printed = console.run(["panic", "issue", str(report)], AGENT)
    assert "gh is not installed: open https://github.com/jessegall/agent-journal/issues/new" in printed.text and "## What held the stops" in printed.text
    hook(app, "PreToolUse", tool_name="Read", tool_input={"file_path": "a.py"})
    assert app.container.get(SessionAgents).top("s1").name != "panicking", "a tool use pops the state"
    assert [hook(app, "Stop")[1].get("decision") for _ in range(4)] == ["block"] * 4 and app.container.get(SessionAgents).top("s1").name != "panicking", "a tool use between stops starts the count again"


def test_a_task_edited_names_one_event_for_each_edit_and_its_holder_is_told_to_read_it_again(app: App):
    from journal.events.rows.task_edited import TaskEdited
    task = Task(environment_id=1, title="the parser", brief="- reads the grammar")
    events = lambda row: [event for event in row.events if isinstance(event, TaskEdited)]
    assert [event.changes for event in events(task.with_(id=1).edited("the lexer", task.brief, 0.0))] == [("title",)], "a title edit names one event"
    assert [event.changes for event in events(task.with_(id=1).edited(task.title, "- reads tokens", 0.0))] == [("brief",)], "a brief edit names one event"
    assert events(task.with_(id=1).edited(task.title, task.brief, 0.0)) == [], "an edit changing neither names none"
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], AGENT)
    console.run(["task", "create", "the parser", "--brief", "reads the grammar", "--start"], AGENT)
    console.run(["task", "create", "the lexer", "--brief", "reads tokens"], USER)
    console.run(["task", "edit", "2", "--brief", "reads tokens and spaces"], USER)
    assert "task 2 changed" not in json.dumps(hook(app, "PreToolUse", tool_name="Read", tool_input={"file_path": "a.py"})[1]), "a task the agent does not hold is not named"
    console.run(["task", "edit", "1", "--title", "the grammar reader"], USER)
    assert "task 1 changed" in json.dumps(hook(app, "PreToolUse", tool_name="Read", tool_input={"file_path": "a.py"})[1]), "the task in hand edited is named at the next tool use"


def test_a_worker_not_running_hears_its_tasks_edit_once_with_its_next_job(app: App):
    from journal.features.workers.support.worker_actions import EDITED_NOTE
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.repositories.workers import Workers
    from journal.models.support.ref import Ref
    tasks, workers, scope = app.container.get(Tasks), app.container.get(Workers), app.container.get(Scope)
    with scope.environment(1):
        worker = workers.save(Worker(environment_id=1, name="Mr. Babbage", brief="b", state=WorkerState.DELIVERED), Actor.system())
        task = tasks.save(Task(environment_id=1, title="the engine", brief="- turns"), Actor.system())
        tasks.handover(task, Ref.build(worker), Actor.system())
    for brief in ("- turns twice", "- turns three times"):
        assert app.console().run(["task", "edit", str(task.id), "--brief", brief], USER).code == 0
    app.runtime().deferred.drain()
    with scope.environment(1):
        assert workers.find(worker.id).edited_task == task.id, "the edit waits on the worker's row, once however many edits came"
    assert EDITED_NOTE.format(task=task.id).startswith(f"Task {task.id} was changed while you were away")


def test_a_session_in_another_folder_than_its_launch_or_whose_folder_is_gone_is_warned_with_the_commands_that_fix_it():
    from journal.features.briefing.briefing_conduct import BriefingConduct
    from journal.features.briefing.support.briefing_data import BriefingData
    from journal.features.tasks.support.tasks_data import TasksData
    tasks = TasksData(current_task=0, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=())
    briefing = lambda **fields: FeatureData({"tasks": tasks, "briefing": BriefingData(is_overview_read=True, environment="development", peer_session_active_at="", rules="", rules_count=0, facts="", reminders="", waiting="", team_history="", launch_folder="/projects/app", **fields)})
    lines = lambda answer: " ".join(nudge.rendered() for nudge in answer.nudges)
    elsewhere = Ready().respond(SessionStarted(source="startup", folder="/projects/app/.claude/worktrees/development").with_data(briefing()), SettingsValue({}), (BriefingConduct,))
    assert "this session runs in /projects/app/.claude/worktrees/development, but development was launched in /projects/app" in lines(elsewhere) and "start development again from /projects/app with `journal`" in lines(elsewhere), "a session in another folder is told, with the commands"
    at_home = Ready().respond(SessionStarted(source="startup", folder="/projects/app/").with_data(briefing()), SettingsValue({}), (BriefingConduct,))
    assert "this session runs in" not in lines(at_home), "the launch's own folder is no warning"
    gone = Ready().respond(Ticked(silence_seconds=5.0, time=100.0).with_data(briefing(is_launch_folder_missing=True)), SettingsValue({"tasks.auto": False}), (BriefingConduct,))
    assert "the folder development was launched in, /projects/app, is gone" in lines(gone) and "`journal message unread`" in lines(gone), "a folder gone is told on the tick, since the session's hooks no longer run"
    assert not Ready().respond(Ticked(silence_seconds=5.0, time=100.0).with_data(briefing()), SettingsValue({"tasks.auto": False}), (BriefingConduct,)).nudges, "a folder still there is no warning"


def test_how_workers_test_sets_whether_a_worker_may_run_a_test_command(app: App):
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.support.agent_token import AgentToken
    hook(app, "SessionStart")
    scope, workers, tasks = app.container.get(Scope), app.container.get(Workers), app.container.get(Tasks)
    with scope.environment(1):
        worker = workers.save(Worker(environment_id=1, name="Mr. Babbage", brief="b", session="w1", token_hash=AgentToken.hashed("tok")), Actor.system())
        tasks.handover(tasks.save(Task(environment_id=1, title="the parser", brief="the parser reads"), Actor.system()), Ref.build(worker), Actor.system())
        workers.save(workers.find(worker.id).ready(1.0), Actor.worker(worker.id))
        app.container.get(SettingRows).set("workers.testing", "The journal runs them", Actor.user(1))

    def worker_runs(command: str):
        data = json.dumps({"hook_event_name": "PreToolUse", "session_id": "w1", "tool_name": "Bash", "tool_input": {"command": command}}).encode()
        request = HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=data, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main", "X-Journal-Actor": f"worker:{worker.id}", "X-Journal-Actor-Token": "tok"})
        try:
            with urlopen(request, timeout=5) as reply:
                return reply.status, json.loads(reply.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())
    for command in ("pytest tests/test_x.py", "npm test", "npx vitest run", "journal suite"):
        status, body = worker_runs(command)
        assert status == 409 and "the journal runs your tests" in body["error"] and "--tests" in body["error"], f"{command} is refused while the journal runs the tests"
    assert worker_runs("ls")[0] == 200, "a command that runs no test passes"
    with scope.environment(1):
        app.container.get(SettingRows).set("workers.testing", "Hand the tests over", Actor.user(1))
    status, body = worker_runs("pytest tests/test_x.py")
    assert status == 409 and "tests are handed over" in body["error"] and "proof" in body["error"], "with Hand the tests over a worker's test command is refused too"
    with scope.environment(1):
        app.container.get(SettingRows).set("workers.testing", "Run the tests it wrote", Actor.user(1))
    assert worker_runs("pytest tests/test_x.py")[0] == 200, "with Run the tests it wrote a worker's test command passes"


def test_the_test_budget_choice_refuses_a_workers_direct_test_run_with_the_line_to_run_it_through_a_turn(app: App):
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.support.agent_token import AgentToken
    hook(app, "SessionStart")
    scope, workers, tasks = app.container.get(Scope), app.container.get(Workers), app.container.get(Tasks)
    with scope.environment(1):
        worker = workers.save(Worker(environment_id=1, name="Mr. Babbage", brief="b", session="w1", token_hash=AgentToken.hashed("tok")), Actor.system())
        tasks.handover(tasks.save(Task(environment_id=1, title="the parser", brief="the parser reads"), Actor.system()), Ref.build(worker), Actor.system())
        workers.save(workers.find(worker.id).ready(1.0), Actor.worker(worker.id))

    def worker_runs(command: str):
        data = json.dumps({"hook_event_name": "PreToolUse", "session_id": "w1", "tool_name": "Bash", "tool_input": {"command": command}}).encode()
        request = HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=data, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main", "X-Journal-Actor": f"worker:{worker.id}", "X-Journal-Actor-Token": "tok"})
        try:
            with urlopen(request, timeout=5) as reply:
                return reply.status, json.loads(reply.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())
    with scope.environment(1):
        app.container.get(SettingRows).set("workers.testing", "Test budget", Actor.user(1))
    for command in ("pytest tests/test_x.py", "npx vitest run"):
        status, body = worker_runs(command)
        assert status == 409 and "journal tests turn" in body["error"], f"{command} is refused with the line that names the turn"
    assert worker_runs("ls")[0] == 200, "a command that runs no test passes"


def test_a_worker_hook_without_its_worker_header_is_still_a_workers_and_never_held_by_the_users_unread_messages(app: App):
    from journal.support.agent_role import AgentRole
    from journal.models.author import Author
    from journal.models.message import Message
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.messages import Messages
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    hook(app, "SessionStart")
    scope = app.container.get(Scope)
    with scope.environment(1):
        workers, tasks = app.container.get(Workers), app.container.get(Tasks)
        worker = workers.save(Worker(environment_id=1, name="Mr. Babbage", brief="b", session="w9"), Actor.system())
        tasks.handover(tasks.save(Task(environment_id=1, title="the parser", brief="the parser reads"), Actor.system()), Ref.build(worker), Actor.system())
        workers.save(workers.find(worker.id).ready(1.0), Actor.worker(worker.id))
        app.container.get(Messages).save(Message(environment_id=1, author=Author.USER, text="for the main agent"), Actor.user(1))
    writes = [hook(app, "PreToolUse", session_id="w9", tool_name="Write", tool_input={"file_path": f"w{n}.py"}) for n in range(8)]
    assert all(status == 200 for status, _ in writes), "a worker's write is allowed with the user's messages unread"
    assert app.container.get(Agents).session_agent("w9").role == AgentRole.WORKER, "its session is a worker's, whatever its hook carried"


def test_with_the_test_budget_the_orchestrator_hears_a_workers_failed_run_in_one_short_line_and_once_when_it_keeps_failing():
    from journal.features.workers.support.test_run_result import TestRunResult
    from journal.features.workers.workers_conduct import WorkersConduct
    from journal.features.workers.workers_options import TEST_BUDGET, WorkersOptions
    budget = SettingsValue({WorkersOptions.TESTING.key: TEST_BUDGET, WorkersOptions.FAILING_RUNS.key: 3, WorkersOptions.TEST_RUN_LINES.key: True})
    worker = Worker(id=3, environment_id=1, name="Lady Lovelace, keeper of the parser", dispatcher="s1")

    # a run as the turn hands it back, ended with the runner's exit line, kept on the worker; what the orchestrator, session s1, hears of it
    def ran(text: str, status: int, settings=budget, session: str = "s1") -> list[str]:
        nonlocal worker
        result = TestRunResult.printed(f"{text}\n__journal_exit {status}", None)
        before = len(worker.events)
        worker = worker.passed_run() if result.is_passed() else worker.failed_run(result.failed, 1.0)
        told = []
        for event in worker.events[before:]:
            told += [n.rendered() for n in Ready().respond(event.reaching(session).with_data(FeatureData({})), settings, (WorkersConduct,)).nudges]
        return told

    assert ran("12 passed in 3.1s", 0) == [], "a passed run is never told"
    failed = ran("tests/test_parser.py F..\n2 failed, 10 passed in 3.4s", 1)
    assert failed == ["worker 3: 2 failed in its test run"], failed
    assert len(failed[0]) <= 120, "one short line"
    assert worker.failing_runs == 1, "the count is kept on the worker"
    assert ran("1 failed, 11 passed in 3s", 1) == ["worker 3: 1 failed in its test run"]
    third = ran("1 error in 2s", 1)
    assert third[0] == "worker 3: 1 failed in its test run"
    assert third[1].startswith("worker 3 failed 3 test runs in a row"), "told once on the third failure in a row"
    assert ran("Traceback (most recent call last)", 1) == ["worker 3: 1 failed in its test run"], "not again on the fourth, and a run that names no count failed one"
    assert ran("12 passed in 3s", 0) == [] and worker.failing_runs == 0, "a passed run starts the count again"
    for _ in range(2):
        ran("1 failed", 1)
    assert ran("1 failed", 1)[1].startswith("worker 3 failed 3 test runs in a row"), "and the notice comes again after the reset"
    quiet = SettingsValue({WorkersOptions.TESTING.key: TEST_BUDGET, WorkersOptions.FAILING_RUNS.key: 3, WorkersOptions.TEST_RUN_LINES.key: False})
    assert ran("12 passed", 0, quiet) == [] and ran("1 failed", 1, quiet) == [], "with the line off a failed run is not told"
    assert ran("1 failed", 1, quiet) == []
    notice = ran("1 failed", 1, quiet)
    assert len(notice) == 1 and notice[0].startswith("worker 3 failed 3 test runs in a row"), "the notice still comes"
    assert ran("1 failed", 1, session="w9") == [], "only the agent that sent the worker hears of it"
    handed = SettingsValue({WorkersOptions.TESTING.key: "Hand the tests over"})
    assert ran("1 failed", 1, handed) == [], "without the test budget nothing is told"


def test_the_orchestrators_load_is_measured_as_one_server_from_its_arrivals_and_clearings():
    from journal.features.workers.support.load_item import LoadItem
    from journal.features.workers.support.load_series import LoadSeries
    series, now = LoadSeries(window_minutes=30, half_life_minutes=10, busy_at=0.8, quiet_at=0.5), 100000.0
    # an item every 3 minutes, each cleared a minute and a half after it came: busy half the time
    steady = [LoadItem(f"workers:{n}", now - 3 * 3600 + n * 180, 1.0, now - 3 * 3600 + n * 180 + 90) for n in range(60)]
    load = series.measured(steady, [], now)
    assert abs(load.arrivals - 20) < 0.5 and abs(load.clearings - 40) < 0.5, "λ 20 an hour arrive, μ 40 an hour of busy time are cleared"
    assert abs(load.rho - 0.5) < 0.02 and abs(load.wait_minutes - 1.5) < 0.01, "ρ = λ/μ, the share of time busy, and W from arrival to clearing"
    assert abs(load.little - 0.5) < 0.02 and load.waiting == 0, "Little's law: λW is the 0.5 that waits on average, and nothing waits now"
    assert load.oldest_first == load.clearings_counted == 10, "each cleared the oldest that waited"
    # an item every minute, each waiting five: the orchestrator never idle, five waiting at a time
    flooded = [LoadItem(f"workers:{n}", now - 2 * 3600 + n * 60, 1.0, now - 2 * 3600 + n * 60 + 300) for n in range(118)]
    busy = series.measured(flooded, [], now)
    assert busy.rho > 0.95 and abs(busy.wait_minutes - 5) < 0.01 and abs(busy.little - 5) < 0.2, "saturated: ρ near 1 and λW near the five that wait"
    assert busy.over_minutes >= 60 and busy.waiting_refs == ("workers:116", "workers:117") and busy.waiting_items == 2, "over 0.8 the whole stretch, and what waits now oldest first"
    # a user's message waits unanswered, weighted 3: dispatches made while the queue grows under a high load count against, one while calm counts for
    oldest = series.measured([*flooded, LoadItem("messages:553", now - 600, 3.0)], [], now)
    assert oldest.waiting_refs[0] == "messages:553" and oldest.waiting == 5.0, "the message is the oldest that waits, weighted 3"
    growing = series.measured([*flooded, LoadItem("messages:553", now - 200, 3.0)], [now - 120, now - 60], now)
    assert growing.dispatches_against == 2 and growing.dispatches_for == 0, "both dispatches made while the queue grew over 0.8"
    quiet = [LoadItem(f"workers:{n}", now - 3 * 3600 + n * 180, 1.0, now - 3 * 3600 + n * 180 + 30) for n in range(60)]
    calm = series.measured(quiet, [now - 300], now)
    assert calm.rho < 0.5 and calm.dispatches_for == 1 and calm.dispatches_against == 0, "a dispatch while the load is low counts for"


def test_a_workers_moves_are_the_items_its_queue_counts_and_an_idle_place_is_none():
    from types import SimpleNamespace
    from journal.features.workers.support.load_items import LoadItems
    from journal.models.support.worker_moves import WorkerMoves
    reader = LoadItems(None, None, SimpleNamespace(holder_task_ids=lambda ref: []), SimpleNamespace(decimal=lambda option: option.default), None)
    moves = WorkerMoves((("clocked in", 10.0), ("clocked out", 100.0), ("sent back", 160.0), ("clocked in", 170.0), ("clocked out", 400.0), ("merged", 460.0), ("sent a job", 470.0), ("ended without clocking out", 900.0)))
    items = reader.worker_items(Worker(id=7, environment_id=1, name="w", moves=moves))
    assert [(item.arrived_at, item.weight, item.cleared_at, item.ended_at, item.is_repeat) for item in items] == [(100.0, 1.0, 0.0, 160.0, False), (400.0, 1.5, 460.0, 0.0, True), (900.0, 1.0, 0.0, 0.0, False)], "a clock-out ended without a clearing by its send-back, the repeat weighted 1.5 cleared by its merge, and the end without a clock-out still waiting"
    assert reader.worker_items(Worker(id=8, environment_id=1, name="w", moves=WorkerMoves((("reported", 50.0), ("sent a job", 80.0))))) == [], "an idle place is no item of the queue; its minutes are read apart"


def test_tasks_added_to_a_plan_leave_the_load_where_it_was(app: App):
    from journal.models.link import Link
    from journal.models.support.ref import Ref
    from journal.repositories.links import Links
    from journal.repositories.tasks import PLAN_LINK
    plans, tasks, links, actor = app.container.get(Plans), app.container.get(Tasks), app.container.get(Links), Actor.system()
    with app.container.get(Scope).environment(1):
        plan = plans.save(Plan(environment_id=1, title="p", state=PlanState.APPROVED), actor)
        before = tasks.unplanned_open_count()
        for number in range(10):
            task = tasks.save(Task(environment_id=1, title=f"t{number}"), actor)
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), kind=PLAN_LINK), actor)
        assert tasks.unplanned_open_count() == before, "ten tasks in a plan are no arrival"
        tasks.save(Task(environment_id=1, title="loose"), actor)
        assert tasks.unplanned_open_count() == before + 1


def test_each_work_mode_keeps_its_own_load_so_a_switch_neither_resets_nor_mixes_them():
    from journal.models.agent import Agent
    from journal.models.support.agent_load import AgentLoad
    agent = Agent(environment_id=1, session="s1", mode="builder", work_queue=AgentLoad(rho=0.4, measured_at=1.0))
    orchestrating = agent.in_mode("orchestrator")
    assert orchestrating.work_queue == AgentLoad(), "a mode not yet measured starts with no figure"
    measured = orchestrating.with_(work_queue=AgentLoad(rho=0.9, measured_at=2.0))
    assert measured.in_mode("builder").work_queue.rho == 0.4, "back in the builder's mode its own figure is there"
    assert measured.in_mode("builder").in_mode("orchestrator").work_queue.rho == 0.9 and measured.in_mode("solo").work_queue == AgentLoad()


def test_a_place_opens_once_the_load_held_over_its_level_and_closes_once_it_held_under_with_each_dwell_honoured_and_each_change_named():
    from journal.features.workers.fitness_options import FitnessOptions
    from dataclasses import replace
    from journal.features.workers.support.place_scaling import PlaceScaling
    from journal.features.workers.workers_conduct import WorkersConduct
    from journal.models.support.agent_load import AgentLoad
    scaling, now = PlaceScaling(up_dwell_minutes=10, down_dwell_minutes=20, floor=2, ceiling=5), 10000.0
    high = AgentLoad(rho=0.92, over_minutes=12, measured_at=now)
    assert scaling.opens(high, 3, now), "over 0.8 for 12 minutes: a place opens"
    assert not scaling.opens(replace(high, over_minutes=6), 3, now), "not before the 10 minute dwell"
    assert not scaling.opens(high, 5, now), "never past the ceiling"
    opened = replace(high, scaled_at=now)
    assert not scaling.opens(replace(opened, over_minutes=17), 4, now + 7 * 60), "a second opening waits the dwell again"
    assert scaling.opens(replace(opened, over_minutes=22), 4, now + 10 * 60)
    low = AgentLoad(rho=0.3, under_minutes=25, measured_at=now)
    assert scaling.closes(low, 3, False, now), "under 0.5 for 25 minutes: a place closes"
    assert not scaling.closes(replace(low, under_minutes=15), 3, False, now), "not before the 20 minute dwell"
    assert not scaling.closes(low, 3, True, now), "never while a worker holds a task"
    assert not scaling.closes(replace(low, waiting=1.0), 3, False, now), "nor while anything waits"
    assert not scaling.closes(low, 2, False, now), "never under the floor"
    agent = Agent(id=1, environment_id=1, session="s1", work_queue=high).place_opened(4, now)
    event = agent.events[-1]
    assert agent.work_queue.scaled_at == now and (event.places, event.opened) == (4, True)
    heard = lambda session: [n.rendered() for n in Ready().respond(event.reaching(session).with_data(FeatureData({})), SettingsValue({FitnessOptions.WARNINGS.key: True}), (WorkersConduct,)).nudges]
    assert heard("s1") == ["your load stayed at 0.92 for 12 minutes: one place more, 4 workers out at once"], heard("s1")
    assert heard("w2") == [], "only the orchestrator hears its places change"
    closed = Agent(id=1, environment_id=1, session="s1", work_queue=low).place_closed(2, now).events[-1]
    assert [n.rendered() for n in Ready().respond(closed.reaching("s1").with_data(FeatureData({})), SettingsValue({FitnessOptions.WARNINGS.key: True}), (WorkersConduct,)).nudges] == ["your load stayed at 0.3 for 25 minutes: one place fewer, 2 workers out at once"]


def test_the_orchestrator_is_asked_for_its_priorities_at_a_phase_start_and_after_the_interval_and_an_unblocking_task_queued_behind_others_is_named_at_once():
    from pathlib import Path
    from journal.events.rows.task_delegated import TaskDelegated
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.plans.support.started_plan import StartedPlan
    from journal.features.workers.support.workers_data import WorkersData
    from journal.features.workers.workers_conduct import WorkersConduct, priorities_lines
    settings = SettingsValue({WorkersOptions.MODE.key: "orchestrator", WorkersOptions.PRIORITIES_MINUTES.key: 45})
    planned = lambda **facts: FeatureData({"plans": PlansData((), StartedPlan(plan_id=5, next_task=8, started_task=7, started_task_briefing="", recent_tasks=(7,), remaining_tasks=3, checkpoint_pause=False, checkpoint_phase=0, testing="", **facts), 0)})
    asked = lambda data, time, settings=settings: [n.rendered() for n in priorities_lines(Ticked(silence_seconds=0.0, time=time).with_data(data), settings)]
    line = lambda phase: f"plan 5, phase {phase}: which open task unblocks the most others, or you (a permission, a missing tool, a failing check, a stalled worker)? Are the queues in that order? answer with journal plan priorities '<the order and why>'"
    assert asked(planned(current_phase=1), 100.0) == [line(1)], "a started plan with no priorities yet asks at once, at the start of its first phase"
    answered = planned(current_phase=1, priorities_phase=1, priorities_at=1000.0)
    assert asked(answered, 1000.0 + 44 * 60) == [], "once answered the line is quiet until the interval has passed"
    assert asked(answered, 1000.0 + 45 * 60) == [line(1)], "after the interval it asks again"
    assert asked(planned(current_phase=2, priorities_phase=1, priorities_at=1000.0), 1100.0) == [line(2)], "a new phase asks at once, without waiting for the interval"
    assert asked(answered, 1000.0 + 90 * 60, SettingsValue({WorkersOptions.MODE.key: "orchestrator", WorkersOptions.PRIORITIES_MINUTES.key: 0})) == [], "with no interval it asks only at a phase start"
    assert asked(planned(current_phase=1), 100.0, SettingsValue({WorkersOptions.MODE.key: "builder"})) == [], "only the orchestrator is asked"
    assert asked(FeatureData({"plans": PlansData((), None, 0)}), 100.0) == [], "and only with a plan started"
    queued = lambda queues: FeatureData({"workers": WorkersData(dispatched_workers=(), idle_workers=(), active_subagents=0, subagents=(), worktrees_root=Path("."), worktrees=(), queues=queues)})
    said = lambda event, data: [n.rendered() for n in Ready().respond(event.reaching("s1").with_data(data), settings, (WorkersConduct,)).nudges]
    unblocking = TaskDelegated(environment_id=1, time=1.0, task_id=9, title="Grant the journal the gh permission", brief="")
    assert said(unblocking, queued({3: (4, 5, 9)})) == ["task 9 unblocks you but is number 3 in worker 3's queue. put it first: journal worker queue 3 9 --first"], "a task that unblocks the orchestrator queued last is named at once"
    assert said(unblocking, queued({3: (9, 4)})) == [], "first in its queue it is not"
    assert said(replace(unblocking, title="The parser", brief="the parser needs read access to the grammar repository"), queued({3: (4, 9)})) != [], "the brief may say it"
    assert said(replace(unblocking, title="The parser"), queued({3: (4, 9)})) == [], "a task that says nothing of unblocking is not named"


def test_a_wait_written_in_words_is_told_to_be_a_block_and_blocked_work_that_stands_still_or_a_plan_with_no_dependencies_is_named():
    from journal.events.agent.tool_starting import ToolStarting
    from journal.features.plans.support.plan_status import PlanStatus
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.features.workers.workers_conduct import unmoved_task_lines, unordered_lines, text_wait_check, text_wait_lines
    settings = SettingsValue({WorkersOptions.MODE.key: "orchestrator", WorkersOptions.STALLED_BLOCK_MINUTES.key: 60, WorkersOptions.BLOCKED_SHARE.key: 0.4, WorkersOptions.UNORDERED_PLAN_TASKS.key: 10})
    builder = SettingsValue({WorkersOptions.MODE.key: "builder"})
    worded = lambda line, settings=settings: [n.rendered() for n in text_wait_check(Ready(), ToolStarting(call=shell(line)), settings).nudges]
    block_line = "you wrote a wait in words; the journal cannot see it. block the task so it opens by itself: journal task block <n> --on task:<m> for a task it waits on, --until '<command>' for anything else"
    assert worded("journal task log 5 'waiting for the API key from the user'") == [block_line], "a log line that says it waits is told to be a block"
    assert worded("journal message send 'task 7 waits on task 4 to merge'") == [block_line], "and a message"
    assert worded("journal task block 7 'waits on the lexer' --on task:4") == [], "a block with --on is the wait itself"
    assert worded("journal task log 5 'the parser reads every rule'") == [], "a log line with no wait in it is not"
    assert worded("journal task log 5 'waiting for the API key'", builder) == [], "only the orchestrator is told"
    assert [n.key for n in text_wait_lines("I am blocked on the deploy until it lands", settings)] == ["workers.make_the_wait_a_block"], "a reply that says it waits is told the same"
    tasks = lambda held, open_count=10: FeatureData({"tasks": TasksData(current_task=0, last_log_line="", paused=(), pause_summary="", blocked=tuple(held), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=(), open_count=open_count, last_moves=held)})
    held = lambda data, time: [n.rendered() for n in unmoved_task_lines(Ticked(silence_seconds=0.0, time=time).with_data(data), settings)]
    still = "these blocked or paused tasks stand still: 3, 5; the plan needs restructuring. check what each waits on, unblock what has arrived, split or reorder what cannot move"
    assert held(tasks({3: 1000.0, 5: 1200.0}), 1000.0 + 59 * 60) == [], "blocked work that moved within the hour is not named"
    assert held(tasks({3: 1000.0, 5: 1200.0}), 1200.0 + 60 * 60) == [still], "once both stood still for the set time they are named with their ids"
    assert held(tasks({3: 1000.0, 5: 1200.0}), 1000.0 + 60 * 60) == [still.replace("3, 5;", "3;")], "only those that stood still"
    assert held(tasks({3: 1000.0, 5: 1200.0}, open_count=2), 1300.0) == [still], "past the set share of the tasks not done they are named at once"
    assert held(tasks({}), 1300.0) == [], "with nothing blocked nothing is said"
    planned = lambda total, done, blocked: FeatureData({"plans": PlansData((), None, 0, started_plans=(PlanStatus(5, "release", 1, 2, done, total, total - done, 0.0, blocked),))})
    unordered = lambda data: [n.rendered() for n in unordered_lines(Ticked(silence_seconds=0.0, time=1.0).with_data(data), settings)]
    assert unordered(planned(12, 2, 0)) == ["plan 5 has 10 open tasks and none blocked on another; its order was likely not thought through. which tasks depend on which? block each on the one it waits for: journal task block <n> --on task:<m>"], "ten open tasks with none blocked asks which depend on which"
    assert unordered(planned(12, 2, 1)) == [], "one blocked on another shows the order was thought of"
    assert unordered(planned(12, 3, 0)) == [], "under ten open tasks nothing is asked"


def test_merged_work_is_scored_for_complexity_and_set_against_the_tier_of_the_model_it_ran_on():
    from journal.features.workers.support.work_complexity import WorkComplexity
    from journal.models.model_tier import ModelTier
    from journal.providers.claude import Claude
    small, large = WorkComplexity(20, 1, 0, 15, 10, 1, True), WorkComplexity(600, 12, 2, 200, 120, 5, True)
    assert small.points() < 4 <= 16 <= large.points() and (small.called_for(), large.called_for()) == (ModelTier.FAST, ModelTier.STRONGEST)
    assert [small.fit(tier).measured for tier in (ModelTier.FAST, ModelTier.GENERAL, ModelTier.STRONGEST)] == ["right", "too strong", "too strong"], "small work on a stronger model than it needs is too strong"
    assert [large.fit(tier).measured for tier in (ModelTier.FAST, ModelTier.GENERAL, ModelTier.STRONGEST)] == ["too weak", "too weak", "right"], "large work sent back again and again on a weaker model is too weak"
    assert WorkComplexity(600, 12, 0, 200, 120, 5, True).fit(ModelTier.GENERAL).measured == "right", "on a weaker model with no send-backs it did the work"
    assert WorkComplexity(0, 0, 0, 5, 1, 0, True).fit(ModelTier.STRONGEST).measured == "", "work with no edit recorded is not judged, so no line is drawn from it"
    assert WorkComplexity(20, 1, 0, 15, 10, 1, False).points() == small.points() + 1, "a brief that names no files makes the work harder"
    assert small.fit(ModelTier.UNKNOWN).measured == "" and [Claude().tier(model) for model in ("claude-haiku-5-5", "sonnet", "claude-opus-5-5", "fable")] == [ModelTier.FAST, ModelTier.GENERAL, ModelTier.STRONGEST, ModelTier.UNKNOWN]


def test_a_watched_progress_that_stands_still_past_twenty_seconds_is_noted_and_one_that_moves_is_not():
    from journal.features.shell.support.progress_stalls import ProgressStalls
    stalls = ProgressStalls()
    for second, fraction in ((0, 0.1), (5, 0.1), (10, 0.2), (15, 0.3)):
        stalls.seen(7, fraction, float(second))
    assert stalls.longest_seconds(7) == 5.0, "a progress that keeps moving stands still only between its steps"
    for second in range(15, 50, 5):
        stalls.seen(7, 0.3, float(second))
    assert stalls.longest_seconds(7) == 30.0, "one that sits at a figure while the run goes on is noted for how long it sat"
    stalls.seen(8, 0.0, 0.0)
    stalls.seen(8, 0.0, 60.0)
    assert stalls.longest_seconds(8) == 0.0, "a run that shows no figure at all is the missing-progress finding's, not this one's"


def test_a_git_commit_or_push_is_never_owed_a_reader_and_every_other_git_step_may_be():
    from journal.features.shell.support.git_writes import GitWrites
    assert all(GitWrites.is_writing(command) for command in ("git commit", "git push")), "the journal marks a commit and a push itself, so neither gets a reader"
    assert not any(GitWrites.is_writing(command) for command in ("git rebase", "git merge", "git log", "git show", "git diff")), "a rebase, a merge and reading the history keep their readers"


def test_the_builder_may_dispatch_queue_and_send_subagents_only_as_its_menu_allows_and_its_line_budget_is_gone_on_purpose():
    from pathlib import Path
    from journal.features.workers.support.workers_data import WorkersData
    from journal.features.workers.workers_conduct import capability_check
    from journal.features.workers.workers_options import WorkersOptions
    def event(line, lines=0):
        from journal.support.command_part import CommandPart
        call = ToolCall.decoded("Bash", {"command": line}, Claude().operation("Bash", {"command": line}), (CommandPart(line, True, False, (), False, ""),))
        return ToolStarting(call=call).with_data(FeatureData({"workers": WorkersData((), (), 0, (), Path("/w"), ())}))
    allowed = {WorkersOptions.BUILDER_DISPATCH_ALLOWED.key: True, WorkersOptions.BUILDER_QUEUE_ALLOWED.key: True, WorkersOptions.BUILDER_SUBAGENTS_ALLOWED.key: True, WorkersOptions.SOLO_SUBAGENTS_ALLOWED.key: True}
    builder = SettingsValue({**allowed, WorkersOptions.MODE.key: "builder"})
    assert capability_check(Ready(), event("journal worker dispatch 1"), builder).refusal is None
    off = SettingsValue({**allowed, WorkersOptions.MODE.key: "builder", WorkersOptions.BUILDER_DISPATCH_ALLOWED.key: False, WorkersOptions.BUILDER_QUEUE_ALLOWED.key: False})
    assert "may not dispatch a worker" in capability_check(Ready(), event("journal worker dispatch 1"), off).refusal.rendered()
    assert "may not queue a worker's next task" in capability_check(Ready(), event("journal worker queue 1 2"), off).refusal.rendered()


def test_the_review_queue_gets_its_first_reviewer_itself_and_the_orchestrator_adds_the_others_up_to_the_most():
    from types import SimpleNamespace
    from journal.features.reviewing.commands.reviewer_command import ReviewerCommand
    from journal.features.reviewing.support.review_queue import ReviewQueue
    from journal.support.rejection import Rejection
    added = []
    dispatch = SimpleNamespace(added=lambda environment_id: added.append(environment_id) or SimpleNamespace(id=len(added)))
    queue = lambda waiting, idle, out: ReviewQueue(SimpleNamespace(queued_reviews=lambda: list(range(waiting))), SimpleNamespace(idle=lambda: list(idle), active=lambda: list(out)), None, None, None, dispatch, None, TimeSource())
    assert len(queue(3, [], []).free_reviewers(1)) == 1, "a queue with no reviewer gets its first"
    assert queue(3, [], ["a"]).free_reviewers(1) == [], "and never a second by itself"
    command = lambda out: ReviewerCommand(SimpleNamespace(active=lambda: list(out)), SimpleNamespace(queued_reviews=lambda: []), dispatch, SimpleNamespace(assigned=lambda environment_id: None), SimpleNamespace(is_enabled=lambda: True), SimpleNamespace(id=1), SimpleNamespace(integer=lambda option: 2))
    assert command(["a"]).add(None, None) == 0, "the orchestrator adds a second"
    try:
        command(["a", "b"]).add(None, None)
    except Rejection as refusal:
        assert "workers.reviewers_most" in str(refusal)
    else:
        raise AssertionError("a third past the most is refused")


def test_a_verdict_wanted_past_the_most_verifiers_waits_for_one_to_come_free():
    from types import SimpleNamespace
    from journal.features.verification.support.verifier_dispatch import VerifierDispatch
    from journal.models.verifier import Verifier
    sent = []
    verifiers = SimpleNamespace(idle=lambda: [v for v in rows if v.state == "judged"], working=lambda: rows)
    rows: list = []
    runner = SimpleNamespace(start=lambda verifier, resume: sent.append((verifier.brief, resume)) or verifier)
    dispatch = VerifierDispatch(verifiers, None, runner, SimpleNamespace(default=lambda: SimpleNamespace(name="claude")), None, SimpleNamespace(integer=lambda option: 1))
    dispatch.judging = lambda verifier, target, resume: (rows.append(verifier), runner.start(verifier, resume))[1]
    target = SimpleNamespace(environment_id=1)
    first = dispatch.dispatched_with(target, "one", "sonnet")
    assert first is not None and dispatch.dispatched_with(target, "two", "sonnet") is None and len(dispatch.waiting) == 1, "past the most the verdict waits"
    rows[0] = rows[0].judged()
    dispatch.released()
    assert dispatch.waiting == [] and [brief for brief, _ in sent] == ["one", "two"], "once one is free the waiting verdict goes to it"


def test_the_merger_runs_one_turn_at_a_time_in_the_order_they_were_asked_for():
    import threading
    import time as timing
    from journal.support.merger import Merger
    from journal.support.part import Part
    merger, spans, lock = Merger(), [], threading.Lock()
    def merge(name: str) -> None:
        with merger.turn():
            began = timing.monotonic()
            timing.sleep(0.05)
            with lock:
                spans.append((name, began, timing.monotonic()))
    threads = []
    for name in ("first", "second", "third"):
        threads.append(threading.Thread(target=merge, args=(name,)))
        threads[-1].start()
        timing.sleep(0.01)
    for thread in threads:
        thread.join(5)
    assert [name for name, _, _ in spans] == ["first", "second", "third"], "turns are served in the order asked for"
    assert all(spans[i][2] <= spans[i + 1][1] for i in range(len(spans) - 1)), "no two turns overlap"
    assert merger.queued() == 0
    assert Part("git merge feature").is_branch_write() and Part("git -C x pull").is_branch_write() and Part("git commit -qm x").is_branch_write(), "a command that writes the branch goes through the merger"
    assert not Part("git status").is_branch_write() and not Part("git log -3").is_branch_write() and not Part("ls").is_branch_write(), "a read of git does not wait"



def test_a_model_outside_the_allowed_ones_of_its_role_is_moved_to_the_nearest_allowed_and_the_line_says_so():
    from types import SimpleNamespace
    from journal.features.workers.support.allowed_models import AllowedModels
    from journal.providers.providers import Providers
    from journal.providers.provider import Provider
    lines = ["claude journal-medior: sonnet, opus", "claude reviewer: sonnet", "claude verifier: haiku, opus", "codex journal-medior: gpt-5.6-sol, gpt-6-astra"]
    allowed = AllowedModels(SimpleNamespace(texts=lambda option: tuple(lines)), Providers())
    assert allowed.clamped("claude", "journal-medior", "sonnet") == ("sonnet", ""), "an allowed model is left alone"
    moved, said = allowed.clamped("claude", "journal-medior", "haiku")
    assert moved == "sonnet" and "haiku is not allowed for journal-medior on claude" in said and "moved to sonnet" in said, "under the minimum it goes up to it"
    assert allowed.clamped("claude", "reviewer", "opus")[0] == "sonnet", "over the maximum it comes down to it"
    assert allowed.clamped("claude", "verifier", "sonnet")[0] == "opus", "between two as near, the stronger"
    assert allowed.clamped("claude", "journal-medior", "claude-haiku-5-5")[0] == "claude-sonnet-5-5", "a full model name keeps all but its tier"
    assert allowed.clamped("claude", "some-worker-profile", "haiku")[0] == "sonnet", "a role with no line takes journal-medior's"
    assert allowed.clamped("codex", "journal-medior", "gpt-6-luna")[0] == "gpt-5.6-sol" and allowed.clamped("codex", "journal-medior", "gpt-6.1-sol")[0] == "gpt-6-astra", "Codex is held to the same from its own list"
    assert allowed.clamped("claude", "journal-medior", "some-unranked-model") == ("some-unranked-model", ""), "a model not on the provider's list is not judged"
    assert allowed.strongest("claude", "verifier") == "opus" and allowed.strongest("claude", "reviewer") == "sonnet"


def test_a_pinned_time_source_is_the_one_moment_of_the_clock_and_every_row_written(app: App):
    from datetime import datetime, timezone
    import time as timing
    from journal.engine.clock import Clock
    from journal.repositories.tasks import Tasks
    from journal.support.time_source import TimeSource
    source = app.container.get(TimeSource)
    moment = 1_800_000_000.0
    source.pin(moment)
    try:
        hook(app, "SessionStart")
        app.console().run(["task", "create", "the pinned task"], AGENT)
        with app.container.get(Scope).environment(1):
            task = app.container.get(Tasks).all()[-1]
        assert app.container.get(Clock).time() == moment, "the clock reads the pinned moment"
        assert task.created_at == datetime.fromtimestamp(moment, timezone.utc) and task.updated_at == task.created_at, "a row written is stamped with it"
    finally:
        source.unpin()
    assert abs(app.container.get(Clock).time() - timing.time()) < 5, "unpinned, the time source is the wall clock and the journal runs as before"


HELPER_CONDUCTS = {
    "worker": ["DemandConduct", "SafetyConduct", "TaskEditConduct"],
    "reviewer": ["DemandConduct", "SafetyConduct"],
    "verifier": ["DemandConduct", "SafetyConduct"],
    "subagent": ["DemandConduct", "SafetyConduct"],
}
HELPER_FLOORS = {"worker": "Void", "reviewer": "Reviewing", "verifier": "Verifying", "subagent": "Researching"}
HELPER_VERBS = {
    "worker": ["await begin", "await clear", "clock-in record", "clock-out record", "doc create", "doc show", "doc update", "fact list", "fact read", "output list", "output read", "output status", "output watch", "proof record", "reader list", "report create", "report show", "rule list", "rule read", "search find", "stuck declare", "task log", "task show", "tests turn", "todo add", "todo check", "todo list", "worker notify", "worker peers", "worker report", "worker send"],
    "reviewer": ["doc show", "fact list", "fact read", "output read", "report show", "review record", "rule list", "rule read", "search find", "task show"],
    "verifier": ["verdict give", "verdict model"],
    "subagent": ["doc show", "fact list", "fact read", "output read", "plan show", "report show", "rule list", "rule read", "search find", "task list", "task show"],
}
HELPER_LISTENERS = {
    "worker": ["HookAnswer", "PluginAgentRelay", "RecordEdit", "SubagentMessageRecord", "SubagentTurnRecord", "WorkerTurnRecord"],
    "reviewer": ["HookAnswer", "PluginAgentRelay", "ReviewerTestFailed", "ReviewerTestPassed"],
    "verifier": ["HookAnswer", "PluginAgentRelay"],
    "subagent": ["HookAnswer", "PluginAgentRelay", "SubagentTurnRecord"],
}


def test_each_helpers_file_alone_says_what_reaches_it_and_a_wrong_file_stops_the_boot(app: App):
    """What each helper role gets, conducts, floor, the verbs it runs and the listeners its hooks reach, is exactly what its file allows; a change to a set is made here on purpose."""
    from journal.events.agent.agent_event import AgentEvent
    from journal.events.bus import Bus
    from journal.features.helper_files_invalid import HelperFilesInvalid
    from journal.features.registry import Registry
    from journal.features.workers.listeners.fitness_record import FitnessRecord
    from journal.helpers.helpers import Helpers
    from journal.helpers.worker_helper import WorkerHelper
    from journal.support.agent_role import AgentRole
    from journal.repositories.setting_rows import SettingRows
    registry, roles = app.container.get(Registry), AgentRole.helpers()
    assert {role.value: sorted(conduct.__name__ for conduct in registry.conducts(role)) for role in roles} == HELPER_CONDUCTS
    assert {role.value: state.__name__ for role, state in registry.floors().items()} == HELPER_FLOORS
    listeners = {listener.registered_class() for kind in StateMachine.event_kinds(AgentEvent) for listener in app.container.get(Bus).listeners(kind)}
    reached = {role.value: sorted({listener.__name__ for listener in listeners if registry.reaches_helper(listener, role)}) for role in roles}
    assert reached == HELPER_LISTENERS, reached
    console = app.console()
    verbs = {role.value: sorted(f"{noun} {verb}" for noun, command in console.commands.items() for verb in console.verbs(command) if registry.runs_verb(type(command), verb, role)) for role in roles}
    assert verbs == HELPER_VERBS, verbs
    assert not registry.reaches_helper(FitnessRecord, AgentRole.WORKER), "a listener no helper's file names, such as the main agent's fitness record, reaches no helper"
    settings = app.container.get(SettingRows)
    with pytest.raises(HelperFilesInvalid, match="the helper role worker has 0 files"):
        Registry(registry.features, settings, (), tuple(helper for helper in Helpers.ALL if helper is not WorkerHelper))
    with pytest.raises(HelperFilesInvalid, match="the helper role worker has 2 files"):
        Registry(registry.features, settings, (), (*Helpers.ALL, type("SecondWorker", (WorkerHelper,), {})))
    from journal.features.edits.listeners.record_edit import RecordEdit
    redundant = type("RedundantWorker", (WorkerHelper,), {"listeners": (*WorkerHelper.listeners, RecordEdit)})
    with pytest.raises(HelperFilesInvalid, match="RedundantWorker names RecordEdit alone, but a feature in its features already gives it to the worker"):
        Registry(registry.features, settings, (), (*(helper for helper in Helpers.ALL if helper is not WorkerHelper), redundant))


def test_every_piece_is_known_by_the_one_feature_that_registers_it_or_by_the_engine(app: App):
    import pytest
    from journal.engine.hook_answer import HookAnswer
    from journal.engine.safety_conduct import SafetyConduct
    from journal.features.double_registration import DoubleRegistration
    from journal.features.feature import Feature
    from journal.features.registry import ENGINE, Registry
    from journal.repositories.setting_rows import SettingRows
    registry = app.container.get(Registry)
    assert all(registry.owning_feature(registered) == feature.name for feature in registry.features for registered in Registry.registered_classes(feature)), "each registered listener, conduct, command, state and job is known by its feature"
    assert {registry.owning_feature(registered) for registered in (HookAnswer, SafetyConduct, *registry.standard_commands)} == {ENGINE}, "the engine's own pieces belong to no feature"
    shared = type("SharedListener", (), {})
    first = type("First", (Feature,), {"name": "first", "listeners": (shared,)})
    second = type("Second", (Feature,), {"name": "second", "listeners": (shared,)})
    with pytest.raises(DoubleRegistration, match="SharedListener is registered by the features first and second"):
        Registry((first, second), app.container.get(SettingRows))


def test_every_helper_rests_on_void_which_holds_every_tool_but_a_journal_command(app: App):
    from journal.engine.support.session_agents import SessionAgents
    from journal.support.agent_role import AgentRole
    sessions = app.container.get(SessionAgents)
    hook(app, "SessionStart")
    floors = {role: [layer["state"] for layer in app.container.get(StatesCatalogue).stack(sessions.helper_agent(f"h-{role.value}", 1, "claude", role)).serialized()] for role in (AgentRole.WORKER, AgentRole.REVIEWER, AgentRole.VERIFIER)}
    assert floors[AgentRole.WORKER] == ["void"], "a worker the journal has not put to work rests on Void alone"
    assert floors[AgentRole.REVIEWER][0] == floors[AgentRole.VERIFIER][0] == "void", "a reviewer and a verifier rest on Void too, their own state over it"
    from journal.engine.states.void import Void
    from journal.events.agent.tool_starting import ToolStarting
    from journal.providers.claude import Claude
    read = Void().respond(ToolStarting(call=Claude().call("Read", {"file_path": "a.py"}, frozenset())).with_data(FeatureData(())), SettingsValue({}))
    assert read.refusal is not None and "you are not at work" in read.refusal.rendered(), "a read in Void is refused with the line that says the helper has no job"
    command = Void().respond(ToolStarting(call=Claude().call("Bash", {"command": "journal clock-in"}, frozenset())).with_data(FeatureData(())), SettingsValue({}))
    assert command.refusal is None, "a journal command passes, so a worker can clock in"


def test_an_agents_line_series_are_kept_by_time_and_read_by_window():
    hour = 3600.0
    agent = Agent(session="s1")
    for minutes, lines in ((0, 10), (50, 20), (100, 30), (170, 40)):
        agent = agent.lines_edited(lines, minutes * 60, minutes * 60 - 3 * hour)
    assert agent.edited_total(170 * 60, hour) == 40 and agent.edited_total(170 * 60, 2 * hour) == 70, "a 60-minute window holds the last pair, a 120-minute one the last two"
    later = agent.lines_edited(5, 200 * 60, 200 * 60 - 3 * hour)
    assert [time for time, _ in later.edited_lines] == [50 * 60, 100 * 60, 170 * 60, 200 * 60], "a pair older than three hours is dropped at the next write"
    committed = agent.lines_committed("abc", 12, 60.0, 0.0).lines_committed("def", 8, 120.0, 0.0)
    assert committed.committed_total(120.0, hour) == 20 and committed.is_sha_counted("abc") and not committed.is_sha_counted("xyz")
    assert agent.first_reported(7, 60.0, 0.0).first_reported(8, 4000.0, 0.0).first_report_count(4000.0, hour) == 1


def test_old_line_pairs_keyed_by_tool_use_are_cleared(connection):
    from journal.db.migrations.timed_line_series import TimedLineSeries
    connection.execute("INSERT INTO agents (environment_id, session, role, state, data, stack, edited_lines, merged_lines, created_at, creator) VALUES (1, 'old', 'main', 'idle', '{}', '[]', ?, ?, '2026-10-26', 'system')", (json.dumps([[12, 40], [30, 5]]), json.dumps([[20, 80]])))
    TimedLineSeries().apply(connection)
    row = connection.all("SELECT edited_lines, merged_lines FROM agents WHERE session = 'old'")[0]
    assert (json.loads(row["edited_lines"]), json.loads(row["merged_lines"])) == ([], []), "pairs keyed by a tool use's number mean nothing as times"


def test_a_commit_counts_its_own_lines_once_per_sha_leaving_out_merges_built_paths_and_a_reformats_excess(app: App):
    from journal.events.announcer import Announcer
    from journal.events.moments.git_committed import GitCommitted
    from journal.events.moments.worker_work_merged import WorkerWorkMerged
    from journal.features.git.support.git_facts import GitFacts
    from journal.features.workers.support.worker_branch import REBUILD_SUBJECT
    hook(app, "SessionStart")
    announcer, agents = app.container.get(Announcer), app.container.get(Agents)
    app.container.get(SettingRows).set("workers.built_paths", ["dist"], Actor.user(1))
    assert GitFacts.added("12\t3\tsrc/parser.py") == ("src/parser.py", 12) and GitFacts.added("-\t-\tlogo.png") == ("logo.png", 0), "a commit's numstat row gives the path and the lines it added"
    commit = lambda sha, lines, subject="the parser": GitCommitted(environment_id=1, session="s1", sha=sha, branch="main", subject=subject, files=len(lines), lines=lines)
    with app.container.get(Scope).environment(1):
        announcer.announce(commit("a1", (("src/parser.py", 30), ("dist/app.js", 900))))
        announcer.announce(commit("a1", (("src/parser.py", 30), ("dist/app.js", 900))))
        assert [lines for _, lines in agents.session_agent("s1").committed_lines] == [30], "a commit announced by the shell's recording and by the head watch counts once, its built path left out"
        announcer.announce(commit("a2", (("src/everything.py", 2000),)))
        assert agents.session_agent("s1").committed_lines[-1][1] == 400, "a 2,000-line reformat counts 400"
        announcer.announce(WorkerWorkMerged(environment_id=1, worker=1, name="Mr. Hook", dispatcher="s1", task=1, next_task=0, time=1.0, lines=40, merged_shas=("w1",)))
        announcer.announce(commit("w1", (("src/footer.py", 40),)))
        announcer.announce(commit("r1", (("dist/app.js", 10),), REBUILD_SUBJECT))
        row = agents.session_agent("s1")
    assert [lines for _, lines in row.committed_lines] == [30, 400] and sum(lines for _, lines in row.merged_lines) == 40, "a worker's commit fast-forwarded into the root counts only as merged, and the rebuild commit counts nothing"


def test_each_modes_band_moves_with_hysteresis_holds_five_minutes_and_leaves_high_on_an_empty_queue():
    from journal.features.workers.support.band_rule import BandRule
    from journal.models.support.pressure_band import PressureBand
    orchestrator, builder = BandRule(0.8, 0.65, 0.5, 0.6, 300, 300), BandRule(0.5, 0.4, 0.3, 0.35, 300, 300)
    high, normal, low = PressureBand.HIGH, PressureBand.NORMAL, PressureBand.LOW
    assert [orchestrator.moved(normal, rho, 600, 0) for rho in (0.79, 0.8, 0.49)] == [normal, high, low], "the orchestrator enters high at 0.8 and low under 0.5"
    assert [orchestrator.moved(high, rho, 600, 0) for rho in (0.66, 0.64)] == [high, normal] and [orchestrator.moved(low, rho, 600, 0) for rho in (0.59, 0.6)] == [low, normal], "and leaves high under 0.65 and low at 0.6"
    assert [builder.moved(normal, rho, 600, 0) for rho in (0.5, 0.29)] == [high, low] and [builder.moved(high, 0.39, 600, 0), builder.moved(low, 0.35, 600, 0)] == [normal, normal], "the builder's band sits on its ceiling of 0.5"
    assert orchestrator.moved(normal, 0.95, 120, 0) == normal, "a band is held five minutes before it changes"
    assert orchestrator.moved(high, 0.95, 60, 300) == normal and orchestrator.moved(high, 0.95, 60, 200) == high, "high is left once the worker queue has stood empty five minutes, held or not"
    assert orchestrator.moved(normal, 0.95, 600, 400) == normal, "high is never entered on a queue empty past the five minutes, however high the smoothed load"


def test_load_held_high_ends_the_minute_nothing_waits_though_the_smoothed_load_is_still_high():
    from journal.features.workers.support.load_item import LoadItem
    from journal.features.workers.support.load_series import LoadSeries
    series = LoadSeries(window_minutes=30, half_life_minutes=10, busy_at=0.8, quiet_at=0.5)
    items = [LoadItem(ref=f"workers:{n}", arrived_at=n * 60.0, weight=1.0) for n in range(20)]
    waiting = series.measured(items, [], 1800.0)
    cleared = series.measured([item.cleared(1800.0) for item in items], [], 1860.0)
    assert waiting.rho >= 0.8 and waiting.over_minutes > 0, waiting
    assert cleared.rho >= 0.8 and cleared.over_minutes == 0.0, "an empty queue ends load held high within one tick, while the smoothed load is still over the line"


def test_a_measure_turns_failing_and_passing_once_each_at_its_levels_a_stretch_is_not_smoothed_and_nothing_to_measure_stays_unmeasured():
    from journal.features.workers.support.closeness import Closeness
    from journal.features.workers.support.measure_range import MeasureRange
    from journal.features.workers.support.measure_source import MeasureSource
    from journal.features.workers.support.measure_spec import MeasureSpec
    from journal.features.workers.support.mode_measures import HIGH_QUEUE, ModeMeasures
    from journal.models.support.measure_state import MeasureState
    share = MeasureSpec("own_code_share", MeasureRange(0.5, 0.6), MeasureSource.code_share, Closeness.share, 4)
    state, changes = MeasureState("own_code_share"), []
    for minute, value in enumerate((0.7, 0.55, 0.49, 0.45, 0.55, 0.59, 0.6, 0.65, 0.52)):
        moved = ModeMeasures.stepped(share, state, value, minute * 60.0)
        if moved.is_failing != state.is_failing:
            changes.append((value, moved.is_failing, moved.changed_at))
        state = moved
    assert changes == [(0.49, True, 120.0), (0.6, False, 360.0)], "failing under 0.5, passing again only at 0.6, once each"
    held = ModeMeasures.stepped(HIGH_QUEUE, ModeMeasures.stepped(HIGH_QUEUE, MeasureState("high_queue_minutes"), 30.0, 0.0), 0.0, 60.0)
    assert held.value == 0.0 and not held.is_failing, "a stretch is taken as it is, never smoothed"
    smoothed = MeasureSpec("idle_places", MeasureRange(5.0, 4.0), MeasureSource.idle_place_minutes, Closeness.minutes, 3, smoothing_minutes=15.0)
    assert 0 < ModeMeasures.stepped(smoothed, ModeMeasures.stepped(smoothed, MeasureState("idle_places"), 10.0, 0.0), 0.0, 60.0).value < 10.0, "idle minutes are smoothed"
    empty = ModeMeasures.stepped(share, state, None, 600.0)
    assert not empty.is_measured and not empty.is_failing, "nothing to measure is unmeasured, never perfect"


def test_the_score_weighs_the_measured_states_and_waits_for_the_warmup():
    from journal.features.workers.support.mode_measures import HIGH_QUEUE, ORCHESTRATOR_SPECS, SCORE_VERSION, ModeMeasures
    from journal.models.support.measure_state import MeasureState
    from journal.models.support.measure_states import MeasureStates
    states = (MeasureState("high_queue_minutes", 35.0, is_measured=True, is_failing=True, measured_at=1800.0), MeasureState("clearing_wait", 2.0, is_measured=True, measured_at=1800.0), MeasureState("delegation", measured_at=1800.0))
    specs = (replace(HIGH_QUEUE, weight=6), *ORCHESTRATOR_SPECS)
    scored = ModeMeasures.scored(MeasureStates("orchestrator", 0.0, states), specs, 1800.0)
    assert scored.is_measured and scored.score == 67 and scored.version == SCORE_VERSION, "held high 35 minutes counts half at weight 6, a short wait whole at weight 3, and the unmeasured delegation is left out"
    assert dict(scored.parts) == {"high_queue_minutes": 50, "clearing_wait": 100}
    assert not ModeMeasures.scored(MeasureStates("orchestrator", 600.0, states), specs, 1800.0).is_measured, "no score until the mode has been measured for the warm-up"


def test_a_minute_tick_records_a_fitness_point_of_the_measure_scoring(app: App):
    from journal.engine.clock import Clock
    from journal.features.workers.support.fitness_point import FitnessPoint
    from journal.features.workers.support.mode_measures import SCORE_VERSION
    from journal.repositories.entries import Entries
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    clock = app.container.get(Clock)
    start = clock.time()
    with app.container.get(Scope).environment(1):
        for minute in (0, 31):
            clock.ticked(Ticked(session="s1", environment_id=1, time=start + minute * 60, silence_seconds=0.0))
        newest = FitnessPoint.parsed(app.container.get(Entries).session_kind_newest("s1", FitnessPoint.KIND, 1)[0].data)
    assert newest.version == SCORE_VERSION and newest.is_measured and newest.score == 100, newest


def test_an_agent_running_across_the_upgrade_starts_unmeasured_with_a_normal_band(app: App):
    from journal.db.connection import Connection
    from journal.engine.clock import Clock
    from journal.features.workers.support.fitness_scoring import FitnessScoring
    from journal.models.support.pressure_band import PressureBand
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    app.container.get(Connection).execute("UPDATE agents SET band = NULL, band_changed_at = NULL, measures = NULL WHERE session = 's1'")
    clock = app.container.get(Clock)
    with app.container.get(Scope).environment(1):
        answers = clock.ticked(Ticked(session="s1", environment_id=1, time=clock.time(), silence_seconds=0.0))
    row = app.container.get(Agents).session_rows("s1")[0]
    assert row.band == PressureBand.NORMAL and row.band_changed_at > 0, "the first band after the upgrade is normal, changed at the first tick"
    assert not app.container.get(FitnessScoring).scored(row).is_measured and not row.measures.failing_keys(), "the score waits its warm-up and no measure is failing"
    assert not [answer for answer in answers if getattr(answer, "nudges", ())], "the tick sends no line"


def test_a_failing_measure_says_its_line_and_says_it_again_only_after_its_nudge_repeat(app: App):
    from journal.engine.nudger import Nudger
    from journal.features.workers.fitness_options import FitnessOptions
    from journal.features.workers.support.workers_data import WorkersData
    from journal.features.workers.workers_conduct import measure_check
    from journal.models.support.agent_load import AgentLoad
    from journal.models.support.measure_state import MeasureState
    from journal.models.support.measure_states import MeasureStates
    from journal.models.support.pressure_band import PressureBand
    from journal.support.time_source import TimeSource
    failing = MeasureStates("orchestrator", 0.0, (MeasureState("high_queue_minutes", 14.0, is_measured=True, is_failing=True, changed_at=400.0, measured_at=1000.0),))
    workers = WorkersData((), (), 0, (), Path("/w"), (), workload=AgentLoad(rho=0.9, waiting_refs=("workers:12",), waiting_items=1, measured_at=1000.0), measures=failing, band=PressureBand.HIGH)
    event = ToolStarting(call=ToolCall(tool="Read", input={}, operation=Claude().operation("Read", {}))).with_data(FeatureData({"workers": workers}))
    lines = measure_check(Ready(), event, SettingsValue({FitnessOptions.WRITE_BLOCK_MINUTES.key: 15, FitnessOptions.WARNINGS.key: True})).nudges
    assert [line.rendered() for line in lines] == ["the worker queue has stood high for 14 minutes. clear worker 12 first, the oldest waiting"], [line.rendered() for line in lines]
    assert measure_check(Ready(), event, SettingsValue({FitnessOptions.WARNINGS.key: False})).nudges == (), "with the warnings off no measure line is said"
    hook(app, "SessionStart")
    agent, nudger, clock = app.container.get(Agents).session_rows("s1")[0], app.container.get(Nudger), app.container.get(TimeSource)
    sent = []
    for second in (1000.0, 1060.0, 1301.0):
        clock.pin(second)
        sent.append(nudger.deliver(agent, lines[0]) is not None)
    clock.unpin()
    assert sent == [True, False, True], "said, held back within its five-minute repeat, and said again after it"


def test_no_band_of_a_mode_holds_two_measure_lines_that_push_opposite_ways():
    from journal.features.workers.support.handout_direction import HandoutDirection
    from journal.features.workers.support.line_bands import LineBands
    from journal.models.support.pressure_band import PressureBand
    for mode in ("builder", "orchestrator", "solo"):
        for band in PressureBand:
            directions = {row.direction for row in LineBands.ROWS if row.mode == mode and band in row.bands}
            assert not {HandoutDirection.INCREASE, HandoutDirection.DECREASE} <= directions, (mode, band)
    assert LineBands.is_allowed("orchestrator", "workers.orchestrator_clear_oldest", PressureBand.HIGH) and not LineBands.is_allowed("orchestrator", "workers.orchestrator_clear_oldest", PressureBand.NORMAL)
    assert ("workers.orchestrator_hand_out", "workers.orchestrator_clear_oldest") in LineBands.opposed_pairs()


def test_a_held_high_worker_queue_opens_a_place_at_the_dwell_and_says_its_line_five_minutes_later(app: App):
    from journal.features.workers.support.load_item import LoadItem
    from journal.features.workers.support.load_series import LoadSeries
    from journal.features.workers.support.mode_measures import ModeMeasures
    from journal.features.workers.support.place_scaling import PlaceScaling
    from journal.models.support.measure_state import MeasureState
    def minutes() -> tuple[int, int, int]:
        spec = app.container.get(ModeMeasures).specs("orchestrator")[0]
        dwell = app.container.get(SettingRows).decimal(WorkersOptions.PLACE_OPENING_MINUTES)
        series, scaling = LoadSeries(30, 10, 0.8, 0.5), PlaceScaling(dwell, 30, 1, 8)
        items = [LoadItem(ref=f"workers:{n}", arrived_at=n * 60.0, weight=1.0) for n in range(40)]
        state, held, opened, failing = MeasureState(spec.key), None, None, None
        for minute in range(40):
            queue = series.measured(items, [], minute * 60.0)
            held = held if held is not None or not queue.over_minutes else minute - queue.over_minutes
            state = ModeMeasures.stepped(spec, state, queue.over_minutes, minute * 60.0)
            opened = opened if opened is not None or not scaling.opens(queue, 1, minute * 60.0) else minute
            failing = failing if failing is not None or not state.is_failing else minute
        return held, opened - held, failing - held
    assert minutes()[1:] == (10, 16), "the place opens ten minutes into the worker queue held high with an item waiting, and the clear line only once fifteen have passed"
    app.console().run(["settings", "set", WorkersOptions.PLACE_OPENING_MINUTES.key, "20"], AGENT)
    assert minutes()[1:] == (20, 26), "a longer dwell moves both"


def test_each_builder_measure_reads_its_series_and_the_builder_that_writes_scores_above_the_one_that_hands_out(app: App):
    from journal.features.workers.support.active_worker_measure import ActiveWorkerMeasure
    from journal.features.workers.support.free_place_measure import FreePlaceMeasure
    from journal.features.workers.support.measure_source import MeasureSource
    from journal.features.workers.support.mode_measures import ModeMeasures
    from journal.models.agent import Agent
    from journal.models.support.measure_state import MeasureState
    from journal.models.support.measure_states import MeasureStates
    from journal.models.support.worker_moves import WorkerMoves
    from journal.models.worker import Worker
    from journal.repositories.tasks import Tasks
    source = lambda agent: MeasureSource(agent, 10000.0, app.container.get(FreePlaceMeasure), app.container.get(ActiveWorkerMeasure), app.container.get(Tasks))
    writer = Agent(environment_id=1, session="s1", committed_lines=((9000.0, 30),), edited_lines=((9500.0, 30),), merged_lines=((8000.0, 20),))
    assert source(writer).code_share() == 0.75, "committed and provisional lines of its own over its own and merged, the last hour"
    assert source(Agent(environment_id=1, session="s1", committed_lines=((9000.0, 20),), merged_lines=((9000.0, 10),))).code_share() is None, "under forty lines there is nothing to measure"
    assert source(Agent(environment_id=1, session="s1", committed_lines=((5000.0, 300),), merged_lines=((9000.0, 40),))).code_share() == 0.0, "lines older than the hour leave the share"
    moves = WorkerMoves((("dispatched", 100.0), ("clocked out", 400.0), ("sent back", 500.0), ("clocked out", 700.0), ("merged", 900.0), ("sent a job", 1000.0)))
    assert ActiveWorkerMeasure.active_spans(Worker(environment_id=1, moves=moves), 1200.0) == [(100.0, 900.0), (1000.0, 1200.0)], "a worker is active from its dispatch through its send-back until its merge, and again from its next job"
    with app.container.get(Scope).environment(1):
        specs = app.container.get(ModeMeasures).specs("builder")
    state = lambda key, value: MeasureState(key, value, is_measured=True, measured_at=3600.0)
    writing = MeasureStates("builder", 0.0, (state("own_code_share", 0.8), state("high_queue_minutes", 0.0), state("active_workers", 0.5), state("completion_rate", 2.0)))
    handing = MeasureStates("builder", 0.0, (state("own_code_share", 0.2), state("high_queue_minutes", 0.0), state("active_workers", 3.0), state("completion_rate", 2.0)))
    assert ModeMeasures.scored(writing, specs, 1800.0).score > ModeMeasures.scored(handing, specs, 1800.0).score, "a builder that writes scores above one with three workers out at once"
    assert "completion_rate" not in dict(ModeMeasures.scored(writing, specs, 1800.0).parts), "the tasks completed an hour are shown, never scored"


def test_each_builder_measure_line_speaks_where_its_measure_fails_in_its_bands_and_nowhere_else():
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.features.workers.fitness_options import FitnessOptions
    from journal.features.workers.support.workers_data import WorkersData
    from journal.features.workers.workers_conduct import measure_check
    from journal.models.support.agent_load import AgentLoad
    from journal.models.support.measure_state import MeasureState
    from journal.models.support.measure_states import MeasureStates
    from journal.models.support.pressure_band import PressureBand
    from journal.models.worker import Worker
    settings = SettingsValue({FitnessOptions.WRITE_BLOCK_MINUTES.key: 15, FitnessOptions.WARNINGS.key: True})
    def said(failing: str, value: float, band: PressureBand, current_task: int = 7, refs=("messages:4", "workers:12"), delivered=(Worker(environment_id=1, id=5),), command: str = "ls") -> list[str]:
        measures = MeasureStates("builder", 0.0, (MeasureState(failing, value, is_measured=True, is_failing=True, measured_at=1000.0),))
        workers = WorkersData((), (), 0, (), Path("/w"), (), workload=AgentLoad(rho=0.9, waiting_refs=refs, waiting_items=len(refs), measured_at=1000.0), measures=measures, band=band, delivered_workers=delivered)
        tasks = TasksData(current_task=current_task, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=())
        event = ToolStarting(call=shell(command)).with_data(FeatureData({"workers": workers, "tasks": tasks}))
        return [line.rendered() for line in measure_check(Ready(), event, settings).nudges]
    assert said("own_code_share", 0.3, PressureBand.NORMAL) == ["your own share of the code this hour is 0.3. write task 7 yourself"]
    assert said("own_code_share", 0.3, PressureBand.LOW) != [] and said("own_code_share", 0.3, PressureBand.HIGH) == [], "it speaks in low and normal, never in high"
    assert said("own_code_share", 0.3, PressureBand.NORMAL, current_task=0) == [], "with no task to write it is silent"
    assert said("high_queue_minutes", 14.0, PressureBand.HIGH) == ["the worker queue has stood high for 14 minutes. take in worker 12 first: check and merge it"], "the oldest worker item, never a message"
    assert said("high_queue_minutes", 14.0, PressureBand.NORMAL) == [] and said("high_queue_minutes", 14.0, PressureBand.HIGH, refs=("messages:4",)) == [], "only in high, and silent with no worker item waiting"
    dispatch = "journal worker dispatch 'Ada' --task 3"
    assert said("active_workers", 3.2, PressureBand.NORMAL, command=dispatch) == ["3.2 workers have been active at once this hour, on average. merge worker 5 next, then hand out the next task"]
    assert said("active_workers", 3.2, PressureBand.HIGH, command="journal worker queue 2 9") != [], "on a queue too, in every band"
    assert said("active_workers", 3.2, PressureBand.NORMAL) == [] and said("active_workers", 3.2, PressureBand.NORMAL, delivered=(), command=dispatch) == [], "only on a dispatch or a queue, and silent with no worker waiting to be checked"


def test_each_orchestrator_measure_reads_its_series_and_the_delegating_orchestrator_scores_above_the_one_that_writes(app: App):
    from journal.features.workers.support.active_worker_measure import ActiveWorkerMeasure
    from journal.features.workers.support.free_place_measure import FreePlaceMeasure
    from journal.features.workers.support.load_item import LoadItem
    from journal.features.workers.support.load_series import LoadSeries
    from journal.features.workers.support.measure_source import MeasureSource
    from journal.features.workers.support.mode_measures import ModeMeasures
    from journal.models.agent import Agent
    from journal.models.support.measure_state import MeasureState
    from journal.models.support.measure_states import MeasureStates
    from journal.repositories.tasks import Tasks
    source = lambda agent: MeasureSource(agent, 10000.0, app.container.get(FreePlaceMeasure), app.container.get(ActiveWorkerMeasure), app.container.get(Tasks))
    series = LoadSeries(30, 10, 0.8, 0.5)
    items = [LoadItem(ref="workers:3", arrived_at=9400.0, weight=1.0), LoadItem(ref="workers:4", arrived_at=9700.0, weight=1.0)]
    waiting = Agent(environment_id=1, session="s1", work_queue=series.measured(items, [], 10000.0))
    assert source(waiting).clearing_wait() == 10.0, "the age of the oldest worker item waiting"
    cleared = Agent(environment_id=1, session="s1", work_queue=series.measured([items[0].cleared(10000.0), items[1]], [], 10060.0))
    assert source(cleared).clearing_wait() == 6.0, "clearing the oldest brings the next one's age at the next measure"
    delegating = Agent(environment_id=1, session="s1", committed_lines=((9000.0, 10),), merged_lines=((9200.0, 60), (9500.0, 30)), first_reports=((9000.0, 1),))
    assert source(delegating).delegation() == 0.1 and source(delegating).report_share() == 0.5, "its own lines among all landed, and first reports per merged task"
    assert source(Agent(environment_id=1, session="s1", committed_lines=((9000.0, 10),), merged_lines=((9500.0, 90),))).delegation() is None, "under two merges in the hour delegation is not measured"
    assert source(Agent(environment_id=1, session="s1")).report_share() is None, "with no merge there are no reports per task to measure"
    with app.container.get(Scope).environment(1):
        specs = app.container.get(ModeMeasures).specs("orchestrator")
    state = lambda key, value: MeasureState(key, value, is_measured=True, measured_at=3600.0)
    common = (state("high_queue_minutes", 0.0), state("clearing_wait", 2.0), state("idle_places", 1.0), state("report_share", 0.3))
    handing = MeasureStates("orchestrator", 0.0, (*common, state("delegation", 0.1)))
    writing = MeasureStates("orchestrator", 0.0, (*common, state("delegation", 0.9)))
    assert ModeMeasures.scored(handing, specs, 1800.0).score > ModeMeasures.scored(writing, specs, 1800.0).score, "an orchestrator that delegates scores above one that writes the work itself"


def test_each_orchestrator_measure_line_speaks_where_its_measure_fails_in_its_bands_and_nowhere_else():
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.features.workers.fitness_options import FitnessOptions
    from journal.features.workers.support.workers_data import WorkersData
    from journal.features.workers.workers_conduct import measure_check
    from journal.models.open_task import OpenTask
    from journal.models.support.agent_load import AgentLoad
    from journal.models.support.measure_state import MeasureState
    from journal.models.support.measure_states import MeasureStates
    from journal.models.support.pressure_band import PressureBand
    from journal.models.worker import Worker
    settings = SettingsValue({FitnessOptions.WRITE_BLOCK_MINUTES.key: 15, FitnessOptions.WARNINGS.key: True, WorkersOptions.WORKER_LIMIT.key: 3})
    task = OpenTask(id=9, title="Fix the cart", brief="", plan_id=0)
    def said(failing: tuple[str, ...], value: float, band: PressureBand, refs=("messages:4", "workers:12"), idle=(), out=(Worker(environment_id=1, id=6),), next_open=task, open_count: int = 3, command: str = "ls") -> list[str]:
        measures = MeasureStates("orchestrator", 0.0, tuple(MeasureState(key, value, is_measured=True, is_failing=True, measured_at=1000.0) for key in failing))
        workers = WorkersData(tuple(out), tuple(idle), 0, (), Path("/w"), (), workload=AgentLoad(rho=0.9, waiting_refs=refs, waiting_items=len(refs), measured_at=1000.0), measures=measures, band=band)
        tasks = TasksData(current_task=0, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=next_open, last_commands=(), open_count=open_count)
        return [line.rendered() for line in measure_check(Ready(), ToolStarting(call=shell(command)).with_data(FeatureData({"workers": workers, "tasks": tasks})), settings).nudges]
    assert said(("high_queue_minutes",), 16.0, PressureBand.HIGH) == ["the worker queue has stood high for 16 minutes. clear worker 12 first, the oldest waiting"]
    assert said(("high_queue_minutes",), 16.0, PressureBand.NORMAL) == [] and said(("high_queue_minutes",), 16.0, PressureBand.HIGH, refs=("messages:4",)) == [], "high only, and silent with no worker item waiting"
    assert said(("clearing_wait",), 9.0, PressureBand.NORMAL) == ["the oldest worker waiting has waited past its range. check worker 12: it waited 9 minutes"]
    assert said(("clearing_wait",), 9.0, PressureBand.LOW) == [] and said(("clearing_wait",), 9.0, PressureBand.HIGH, refs=()) == [], "normal and high only, silent with no worker waiting"
    assert said(("delegation", "idle_places"), 0.6, PressureBand.LOW, idle=(Worker(environment_id=1, id=3),)) == ["too little of the work is handed out. queue task 9 to worker 3"], "one line for both measures, to an idle worker first"
    assert said(("delegation",), 0.6, PressureBand.NORMAL) == ["too little of the work is handed out. dispatch a worker on task 9"], "else to a new worker while a place is free"
    assert said(("delegation",), 0.6, PressureBand.HIGH) == [] and said(("delegation",), 0.6, PressureBand.NORMAL, next_open=None) == [], "never in high, and silent with no task to hand out"
    full = tuple(Worker(environment_id=1, id=n) for n in (6, 7, 8))
    assert said(("idle_places",), 7.0, PressureBand.NORMAL, out=full) == [], "silent with no free place and no idle worker"
    assert said(("report_share",), 0.5, PressureBand.HIGH) == ["your workers report once for every 2.0 tasks merged. queue worker 6 its next tasks with --report queue"], "in every band"
    assert said(("report_share",), 0.5, PressureBand.NORMAL, out=()) == [] and said(("report_share",), 0.5, PressureBand.NORMAL, open_count=1) == [], "silent with no worker out or under two open tasks"
    dispatch = "journal worker dispatch 'Ada' --task 9"
    assert said((), 0.0, PressureBand.HIGH, command=dispatch) == ["this dispatch comes while the worker queue stands high and worker 12 waits. check and merge worker 12 next"], "a line on a dispatch in high, never a refusal"
    assert said((), 0.0, PressureBand.NORMAL, command=dispatch) == [] and said((), 0.0, PressureBand.HIGH, command="journal worker queue 6 9") == [], "only on a dispatch, only in high"


def test_the_orchestrator_share_columns_are_dropped_from_a_database_that_holds_them(connection):
    from journal.db.migrations.orchestrator_share_columns_drop import DROPPED_COLUMNS, OrchestratorShareColumnsDrop
    for column in DROPPED_COLUMNS:
        connection.execute(f"ALTER TABLE agents ADD COLUMN {column} TEXT")
    connection.execute("INSERT INTO agents (environment_id, session, role, state, data, stack, created_at, creator, reuse_uses) VALUES (1, 's1', 'main', 'idle', '{}', '[]', '2026-10-26', 'system', '[3, 4]')")
    OrchestratorShareColumnsDrop().apply(connection)
    OrchestratorShareColumnsDrop().apply(connection)
    columns = {row["name"] for row in connection.all("PRAGMA table_info(agents)")}
    assert not columns & set(DROPPED_COLUMNS) and connection.all("SELECT session FROM agents")[0]["session"] == "s1", "the columns go, the row stays, and a second run finds nothing to drop"


def test_every_mode_is_scored_on_how_long_its_oldest_message_waits_and_solo_on_that_alone():
    from journal.features.workers.support.load_item import LoadItem
    from journal.features.workers.support.load_series import LoadSeries
    from journal.features.workers.support.measure_source import MeasureSource
    from journal.features.workers.support.mode_measures import COMPLETION_RATE, MESSAGE_WAIT, ModeMeasures
    from journal.models.agent import Agent
    from journal.models.support.measure_state import MeasureState
    from journal.models.support.measure_states import MeasureStates
    queue = LoadSeries(30, 10, 0.8, 0.5).measured([LoadItem(ref="messages:553", arrived_at=9280.0, weight=3.0)], [], 10000.0)
    assert MeasureSource(Agent(environment_id=1, session="s1", message_queue=queue), 10000.0, None, None, None).message_wait_minutes() == 12.0, "a message unanswered for twelve minutes"
    state = ModeMeasures.stepped(MESSAGE_WAIT, MeasureState("message_wait"), 12.0, 10000.0)
    scored = ModeMeasures.scored(MeasureStates("solo", 0.0, (state, MeasureState("completion_rate", 4.0, is_measured=True, measured_at=10000.0))), (MESSAGE_WAIT, COMPLETION_RATE), 1800.0)
    assert state.is_failing and scored.score == 72 and dict(scored.parts) == {"message_wait": 72}, "twelve minutes is off its five, scored on the minutes kind, and the tasks closed are shown only"


def test_the_tool_use_columns_are_dropped_from_a_database_that_holds_them(connection):
    from journal.db.migrations.tool_use_columns_drop import DROPPED_COLUMNS, ToolUseColumnsDrop
    for column in DROPPED_COLUMNS:
        connection.execute(f"ALTER TABLE agents ADD COLUMN {column} TEXT")
    connection.execute("INSERT INTO agents (environment_id, session, role, state, data, stack, created_at, creator, handover_uses) VALUES (1, 's1', 'main', 'idle', '{}', '[]', '2026-10-26', 'system', '[3]')")
    connection.execute("INSERT INTO entries (environment_id, kind, actor, data, created_at, creator) VALUES (1, 'workload_level', 'system', '{}', '2026-10-26', 'system')")
    ToolUseColumnsDrop().apply(connection)
    ToolUseColumnsDrop().apply(connection)
    columns = {row["name"] for row in connection.all("PRAGMA table_info(agents)")}
    assert not columns & set(DROPPED_COLUMNS) and connection.all("SELECT session FROM agents")[0]["session"] == "s1", "the columns go and the row stays"
    assert not connection.all("SELECT id FROM entries WHERE kind = 'workload_level'"), "and the load level entries go"


def test_the_settings_rows_of_removed_options_are_deleted_and_the_settings_read_cleanly_before_and_after(app: App):
    from journal.db.connection import Connection
    from journal.db.migrations.removed_settings_drop import REMOVED_KEYS, RemovedSettingsDrop
    connection = app.container.get(Connection)
    for key in REMOVED_KEYS[:3]:
        connection.execute("INSERT INTO settings (environment_id, key, value, created_at, creator) VALUES (0, ?, '5', '2026-10-26', 'system')", (key,))
    assert app.console().run(["settings", "list"], AGENT).code == 0, "the settings read with stale rows in place"
    RemovedSettingsDrop().apply(connection)
    assert not connection.all("SELECT key FROM settings WHERE key = ?", (REMOVED_KEYS[0],)), "the stale rows are gone"
    listed = app.console().run(["settings", "list"], AGENT)
    assert listed.code == 0 and REMOVED_KEYS[0] not in listed.text, "and the list names none of them"


def test_a_change_of_mode_starts_the_measures_fresh_so_no_line_of_the_old_mode_is_said_and_old_merges_are_not_counted(app: App):
    from journal.features.tasks.support.tasks_data import TasksData
    from journal.features.workers.fitness_options import FitnessOptions
    from journal.features.workers.support.mode_measures import ModeMeasures
    from journal.features.workers.support.workers_data import WorkersData
    from journal.features.workers.workers_conduct import measure_check
    from journal.models.agent import Agent
    from journal.models.support.measure_state import MeasureState
    from journal.models.support.measure_states import MeasureStates
    from journal.models.support.pressure_band import PressureBand
    failing = MeasureStates("builder", 0.0, (MeasureState("own_code_share", 0.2, is_measured=True, is_failing=True, measured_at=9000.0),))
    agent = Agent(environment_id=1, session="s1", committed_lines=((9000.0, 10),), merged_lines=((9100.0, 60), (9200.0, 60)), measures=failing, band=PressureBand.HIGH)
    with app.container.get(Scope).environment(1):
        fresh = app.container.get(ModeMeasures).worked(agent, "orchestrator", 10000.0)
        later = app.container.get(ModeMeasures).worked(agent.measures_worked(fresh), "orchestrator", 10600.0)
    assert fresh.mode == "orchestrator" and fresh.started_at == 10000.0 and not fresh.failing_keys(), "the new mode's measures start fresh, none failing"
    assert not later.state("delegation").is_measured, "the merges taken in before the switch are not counted for the new mode"
    workers = WorkersData((), (), 0, (), Path("/w"), (), measures=fresh, band=PressureBand.NORMAL)
    tasks = TasksData(current_task=7, last_log_line="", paused=(), pause_summary="", blocked=(), blocked_without_wait=(), blocked_without_wait_summary="", broken_waits=(), broken_waits_summary="", first_pause_reason="", next_open=None, last_commands=())
    event = ToolStarting(call=shell("ls")).with_data(FeatureData({"workers": workers, "tasks": tasks}))
    assert measure_check(Ready(), event, SettingsValue({FitnessOptions.WARNINGS.key: True})).nudges == (), "no line of the old mode is said after the switch"


def test_a_worker_queue_failing_past_its_block_minutes_blocks_writes_until_the_oldest_is_cleared_and_never_its_own_remedy():
    from journal.features.workers.fitness_options import FitnessOptions
    from journal.features.workers.support.workers_data import WorkersData
    from journal.features.workers.workers_conduct import measure_check
    from journal.models.support.agent_load import AgentLoad
    from journal.models.support.measure_state import MeasureState
    from journal.models.support.measure_states import MeasureStates
    from journal.models.support.pressure_band import PressureBand
    on = SettingsValue({FitnessOptions.WARNINGS.key: True, FitnessOptions.WRITE_BLOCK_MINUTES.key: 15})
    edit = Claude().call("Edit", {"file_path": "/w/a.py", "old_string": "x", "new_string": "y"}, frozenset())
    def answer(call, failing: bool = True, time: float = 1000.0, settings=on):
        state = MeasureState("high_queue_minutes", 20.0, is_measured=True, is_failing=failing, changed_at=0.0, measured_at=time)
        workers = WorkersData((), (), 0, (), Path("/w"), (), workload=AgentLoad(rho=0.9, waiting_refs=("workers:12",), waiting_items=1, measured_at=time), measures=MeasureStates("orchestrator", 0.0, (state,)), band=PressureBand.HIGH)
        return measure_check(Ready(), ToolStarting(call=call, time=time).with_data(FeatureData({"workers": workers})), settings)
    assert answer(edit).refusal.rendered() == "the worker queue has stood high for 20 minutes. clear worker 12 first, the oldest waiting", "past fifteen minutes failing, a write waits with the line as its remedy"
    assert answer(edit, time=600.0).refusal is None, "within the block minutes the line is said, the write goes through"
    assert answer(shell("journal worker merge 12")).refusal is None and answer(shell("cat src/a.py")).refusal is None, "the merge it names and every read go through"
    assert answer(edit, failing=False).refusal is None, "once the queue is clear the next write goes through"
    assert answer(edit, settings=SettingsValue({FitnessOptions.WARNINGS.key: False})).refusal is None, "with the fitness warnings off nothing is blocked"


def test_with_the_fitness_warnings_off_the_score_is_still_kept_while_no_measure_speaks_or_blocks(app: App):
    from journal.engine.clock import Clock
    from journal.features.workers.fitness_options import FitnessOptions
    from journal.features.workers.support.fitness_point import FitnessPoint
    from journal.repositories.entries import Entries
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    app.container.get(SettingRows).set(FitnessOptions.WARNINGS.key, False, Actor.user(1))
    clock = app.container.get(Clock)
    start = clock.time()
    with app.container.get(Scope).environment(1):
        for minute in (0, 31):
            clock.ticked(Ticked(session="s1", environment_id=1, time=start + minute * 60, silence_seconds=0.0))
        newest = FitnessPoint.parsed(app.container.get(Entries).session_kind_newest("s1", FitnessPoint.KIND, 1)[0].data)
    assert newest.is_measured, "the measures are worked out and the score kept with the warnings off"
    told = json.dumps(hook(app, "PreToolUse", tool_name="Edit", tool_input={"file_path": str(app.config.root / "a.py"), "old_string": "x", "new_string": "y"})[1])
    assert "worker queue has stood high" not in told and "decision" not in told, "and no measure line is said and no write waits"


def test_stored_helper_stacks_move_onto_void(connection):
    from journal.db.migrations.void_helper_floors import VoidHelperFloors
    rows = [
        ("worker", "working", '{"task_id": 7}', json.dumps([{"state": "duty", "data": {}}, {"state": "working", "data": {"task_id": 7, "logged_at": 1.0}}])),
        ("worker", "duty", "{}", "[]"),
        ("reviewer", "reviewing", "{}", json.dumps([{"state": "reviewing", "data": {}}])),
        ("main", "duty", "{}", json.dumps([{"state": "duty", "data": {}}])),
    ]
    for role, state, data, stack in rows:
        connection.execute("INSERT INTO agents (environment_id, session, role, state, data, stack, created_at, creator) VALUES (1, ?, ?, ?, ?, ?, '2026-10-26', 'system')", (f"s-{role}-{state}", role, state, data, stack))
    VoidHelperFloors().apply(connection)
    stacks = [[layer["state"] for layer in json.loads(row["stack"])] for row in connection.all("SELECT stack FROM agents ORDER BY id")]
    assert stacks == [["void", "working_task"], ["void"], ["void", "reviewing"], ["idle"]], stacks
    assert json.loads(connection.all("SELECT stack FROM agents ORDER BY id")[0]["stack"])[1]["data"] == {"task_id": 7}, "the worker keeps the task it worked on"


def test_a_helper_is_put_to_work_on_each_path_and_the_engine_imports_no_feature_to_do_it(app: App):
    from pathlib import Path
    from journal.support.agent_role import AgentRole
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    hook(app, "SessionStart")
    scope, workers, tasks, agents = app.container.get(Scope), app.container.get(Workers), app.container.get(Tasks), app.container.get(Agents)
    top = lambda session: agents.session_agent(session).stack[-1]["state"]
    with scope.environment(1):
        early = workers.save(Worker(environment_id=1, name="Mr. Early", brief="e", session="we"), Actor.system())
        tasks.handover(tasks.save(Task(environment_id=1, title="the parser", brief="b"), Actor.system()), Ref.build(early), Actor.system())
        workers.save(workers.find(early.id).ready(1.0), Actor.worker(early.id))
        agents.save(Agent(environment_id=1, session="we", provider="claude", state="void", role=AgentRole.WORKER), Actor.system())
    assert top("we") == "working_task", "a worker that clocked in before its session had a row is put to work when the row is made"
    with scope.environment(1):
        workers.save(workers.find(early.id).delivered(2.0), Actor.worker(early.id))
    assert top("we") == "void", "its delivery returns it to Void"
    with scope.environment(1):
        workers.save(workers.find(early.id).with_(state=WorkerState.DISPATCHED), Actor.system())
        workers.save(workers.find(early.id).ready(3.0), Actor.worker(early.id))
    assert top("we") == "working_task", "a worker sent back and clocked in again is put to work again"
    engine = Path(__file__).resolve().parents[1] / "src" / "journal" / "engine"
    assert not [path.name for path in engine.rglob("*.py") if "journal.features" in path.read_text()], "the engine imports no feature to put a helper to work"


@dataclass(frozen=True)
class Beneath(BaseState):
    name = "beneath_probe"
    count: int = 0

    def on_pause(self, settings: SettingsValue) -> tuple[Nudge, ...]:
        return (Nudge("engine", "paused", "paused"),)

    def on_resume(self, data: FeatureData, settings: SettingsValue) -> tuple[Nudge, ...]:
        return (Nudge("engine", "resumed", "resumed"),)


@dataclass(frozen=True)
class Above(BaseState):
    name = "above_probe"
    count: int = 0

    def on_enter(self, typist: Typist) -> None:
        typist.pause()

    def on_exit(self, typist: Typist) -> None:
        typist.resume()

    def on_push(self, settings: SettingsValue) -> tuple[Nudge, ...]:
        return (Nudge("engine", "pushed", "pushed"),)

    def on_pop(self, settings: SettingsValue) -> tuple[Nudge, ...]:
        return (Nudge("engine", "popped", "popped"),)


def test_every_lifecycle_handler_runs_when_the_same_event_also_updates_the_state_it_moves_from(app: App):
    from journal.support.agent_role import AgentRole
    machine, settings, data = app.container.get(StateMachine), SettingsValue({}), FeatureData(())
    keys = lambda answer: [nudge.key for nudge in answer.nudges]
    plain_push = machine.answer_moves(Stack((Beneath(),)), Beneath().push(Above()), AgentRole.MAIN, settings, data)
    assert keys(plain_push) == ["engine.paused", "engine.pushed"]
    updated_push = machine.answer_moves(Stack((Beneath(),)), Beneath(count=1).push(Above()), AgentRole.MAIN, settings, data)
    assert keys(updated_push) == ["engine.paused", "engine.pushed"], "a push in the event that also updates the state beneath still pauses it and pushes"
    assert updated_push.stack.states == (Beneath(count=1), Above()), "and keeps the update"
    plain_pop = machine.answer_moves(Stack((Beneath(), Above())), Above().pop(), AgentRole.MAIN, settings, data)
    assert keys(plain_pop) == ["engine.popped", "engine.resumed"]
    updated_pop = machine.answer_moves(Stack((Beneath(), Above())), Above(count=1).pop(), AgentRole.MAIN, settings, data)
    assert keys(updated_pop) == ["engine.popped", "engine.resumed"], "a pop in the event that also updates the state it leaves still pops it and resumes the one beneath"
    entering, leaving = Typist(), Typist()
    updated_push.stack.replace(Stack((Beneath(),)), entering)
    updated_pop.stack.replace(Stack((Beneath(), Above())), leaving)
    assert (entering.moves, leaving.moves) == (["pause"], ["resume"]), "on_enter and on_exit run on the stack a combined move leaves"


def test_a_helper_compacted_mid_task_returns_to_its_job_with_nothing_of_the_main_agent(app: App):
    from journal.support.agent_role import AgentRole
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    hook(app, "SessionStart")
    scope, workers, tasks, agents = app.container.get(Scope), app.container.get(Workers), app.container.get(Tasks), app.container.get(Agents)
    states = lambda: [layer["state"] for layer in agents.session_agent("wc").stack]
    with scope.environment(1):
        agents.save(Agent(environment_id=1, session="wc", provider="claude", state="void", role=AgentRole.WORKER), Actor.system())
        worker = workers.save(Worker(environment_id=1, name="Mr. Compact", brief="c", session="wc"), Actor.system())
        tasks.handover(tasks.save(Task(environment_id=1, title="the printer", brief="b"), Actor.system()), Ref.build(worker), Actor.system())
        workers.save(workers.find(worker.id).ready(1.0), Actor.worker(worker.id))
    hook(app, "PreCompact", session_id="wc")
    assert states() == ["void", "working_task", "compacting"], "the compaction goes over the helper's job"
    started = hook(app, "SessionStart", session_id="wc", source="compact")[1]
    assert states() == ["void", "working_task"], "and pops back to it, never pushing the main agent's overview"
    context = json.dumps(started)
    assert "environment overview" not in context and "read the journal skill" not in context, "no overview and no main skill debt reach the helper"
    assert hook(app, "PreToolUse", session_id="wc", tool_name="Read", tool_input={"file_path": "a.py"})[0] == 200, "its next read goes through as before the compaction"


def test_helpers_at_work_when_the_journal_restarts_on_the_new_code_keep_working(app: App):
    from journal.db.connection import Connection
    from tests.main_journal import main_journal
    hook(app, "SessionStart")
    connection = app.container.get(Connection)
    old_rows = [
        ("worker", "working", json.dumps([{"state": "duty", "data": {}}, {"state": "working", "data": {"task_id": 7, "logged_at": 1.0}}])),
        ("reviewer", "reviewing", json.dumps([{"state": "reviewing", "data": {}}])),
    ]
    for role, state, stack in old_rows:
        connection.execute("INSERT INTO agents (environment_id, session, role, state, data, stack, created_at, creator) VALUES (1, ?, ?, ?, '{}', ?, '2026-10-26', 'system')", (f"up-{role}", role, state, stack))
    connection.execute("DELETE FROM migrations WHERE number = 59")
    restarted = main_journal(Config(app.config.root, port=0))
    agents, catalogue = restarted.container.get(Agents), restarted.container.get(StatesCatalogue)
    stacks = {role: [state.name for state in catalogue.stack(agents.session_agent(f"up-{role}")).states] for role, _, _ in old_rows}
    assert stacks == {"worker": ["void", "working_task"], "reviewer": ["void", "reviewing"]}, "a worker mid-task keeps its job and a reviewer mid-review keeps reviewing across the restart"
    assert catalogue.stack(agents.session_agent("up-worker")).top().task_id == 7, "on the task it held"


def test_a_session_the_journal_has_not_bound_is_never_a_main_agent(app: App):
    from journal.support.agent_role import AgentRole
    from journal.models.worker import Worker
    from journal.repositories.workers import Workers
    from journal.support.agent_token import AgentToken
    hook(app, "SessionStart")
    assert app.container.get(Agents).session_agent("s1").role == AgentRole.MAIN, "the launch's own session is the main agent"
    with app.container.get(Scope).environment(1):
        worker = app.container.get(Workers).save(Worker(environment_id=1, name="Mr. Morse", brief="m", token_hash=AgentToken.hashed("tok")), Actor.system())
    raw = f"JOURNAL_ENV=main\0JOURNAL_SESSION=fresh-w\0JOURNAL_ACTOR=worker:{worker.id}\0JOURNAL_ACTOR_TOKEN=tok\0JOURNAL_AGENT_SHELL=1\0\0echo hi\n"
    request = HttpRequest(f"http://127.0.0.1:{app.server().port}/shell/run", data=raw.encode(), method="POST", headers={"Content-Type": "application/octet-stream", "X-Journal-Env": "main", "X-Journal-Cwd": str(app.config.root), "X-Journal-Shell": "sh"})
    with urlopen(request, timeout=10) as reply:
        assert reply.read().decode().rstrip().endswith("__journal_exit 0")
    shelled = app.container.get(Agents).session_agent("fresh-w")
    assert shelled.role == AgentRole.WORKER and shelled.state == "void", "a worker's command from a session not seen yet makes the worker's row on Void, never a main one"
    data = json.dumps({"hook_event_name": "PreToolUse", "session_id": "early-w", "tool_name": "Read", "tool_input": {"file_path": "a.py"}}).encode()
    with app.container.get(Scope).environment(1):
        early = app.container.get(Workers).save(Worker(environment_id=1, name="Mr. Bell", brief="b", token_hash=AgentToken.hashed("tok")), Actor.system())
    hooked = HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=data, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main", "X-Journal-Actor": f"worker:{early.id}", "X-Journal-Actor-Token": "tok"})
    with pytest.raises(HTTPError) as refused:
        urlopen(hooked, timeout=5)
    answer = refused.value.read().decode()
    assert app.container.get(Agents).session_agent("early-w").role == AgentRole.WORKER, "a worker's hook before its bind is bound as the worker"
    assert "you are not at work" in answer and "environment overview" not in answer, "and is answered by Void, with no main line"


def test_a_helpers_command_events_reach_only_the_listeners_its_file_allows(app: App):
    from journal.events.agent.command_ended import CommandEnded
    from journal.events.agent.impasse_report import ImpasseReport
    from journal.features.registry import Registry
    from journal.helpers.helper_listeners import HelperListeners
    from journal.support.agent_role import AgentRole
    from journal.repositories.messages import Messages
    hook(app, "SessionStart")
    with app.container.get(Scope).environment(1):
        app.container.get(Agents).save(Agent(environment_id=1, session="hl", provider="claude", state="reviewing", role=AgentRole.REVIEWER), Actor.system())
    funnel, registry = app.container.get(HelperListeners), app.container.get(Registry)
    ended = CommandEnded(output=1, status=0).placed("hl", 1, "claude", None, 1.0)
    heard = {listener.registered_class() for listener in funnel.listeners(ended)}
    assert heard and all(registry.reaches_helper(listener, AgentRole.REVIEWER) for listener in heard), "a reviewer's command end reaches the engine's listeners and those its file allows, nothing else"
    stuck = ImpasseReport(reason="lost").placed("hl", 1, "claude", None, 1.0)
    main_stuck = ImpasseReport(reason="lost").placed("s1", 1, "claude", None, 1.0)
    assert "ImpasseCard" not in {listener.registered_class().__name__ for listener in funnel.listeners(stuck)} and "ImpasseCard" in {listener.registered_class().__name__ for listener in funnel.listeners(main_stuck)}, "a reviewer's stuck event makes no main card, the main agent's does"
    with app.container.get(Scope).environment(1):
        before = len(app.container.get(Messages).all())
    assert app.console().run(["stuck", "lost"], Caller.agent("main", "s1", "claude").subagent_caller()).code == 1, "a researcher's stuck is refused by its file"
    with app.container.get(Scope).environment(1):
        assert len(app.container.get(Messages).all()) == before, "and makes no card"


def test_a_workers_hook_runs_its_allowed_listeners_and_no_deferred_main_recorder(app: App):
    from journal.events.agent.tool_finished import ToolFinished
    from journal.helpers.helper_listeners import HelperListeners
    from journal.models.worker import Worker
    from journal.providers.claude import Claude
    from journal.repositories.edits import Edits
    from journal.repositories.workers import Workers
    from journal.support.agent_token import AgentToken
    hook(app, "SessionStart")
    with app.container.get(Scope).environment(1):
        worker = app.container.get(Workers).save(Worker(environment_id=1, name="Mr. Escher", brief="e", session="wd", token_hash=AgentToken.hashed("tok")), Actor.system())
    target = app.config.root / "drawn.py"
    target.write_text("HANDS = 2\n")
    data = json.dumps({"hook_event_name": "PostToolUse", "session_id": "wd", "tool_name": "Write", "tool_input": {"file_path": str(target), "content": "HANDS = 2\n"}, "tool_response": {}}).encode()
    request = HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=data, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main", "X-Journal-Actor": f"worker:{worker.id}", "X-Journal-Actor-Token": "tok"})
    with urlopen(request, timeout=5) as reply:
        assert reply.status == 200
    app.runtime().deferred.drain()
    with app.container.get(Scope).environment(1):
        assert app.container.get(Edits).agent_edits("wd", 0.0, 10), "the edit recorder its file allows runs on the worker's hook"
    finished = ToolFinished(call=Claude().call("Write", {"file_path": str(target), "content": "x"}, frozenset()), output="").placed("wd", 1, "claude", None, 1.0)
    reached = {listener.registered_class().__name__ for listener in app.container.get(HelperListeners).listeners(finished)}
    assert "RecordEdit" in reached and not reached & {"LoadRecord", "FitnessRecord", "LoadTickRecord"}, "while the main agent's deferred recorders never hear it"


def test_a_helper_reads_only_the_data_parts_of_features_its_file_turns_on(app: App):
    from journal.engine.support.data_readers import DataReaders
    from journal.engine.support.helper_part_violation import HelperPartViolation
    from journal.features.workers.workers_part import WorkersPart
    from journal.features.tasks.tasks_part import TasksPart
    from journal.support.agent_role import AgentRole
    hook(app, "SessionStart")
    agents, readers = app.container.get(Agents), app.container.get(DataReaders)
    with app.container.get(Scope).environment(1):
        worker = agents.save(Agent(environment_id=1, session="dw", provider="claude", state="void", role=AgentRole.WORKER), Actor.system())
        reviewer = agents.save(Agent(environment_id=1, session="dr", provider="claude", state="reviewing", role=AgentRole.REVIEWER), Actor.system())
    assert readers.agent_data(worker).part(WorkersPart).session_workers == (), "a worker reads the workers part its file turns on"
    assert readers.agent_data(worker).part(TasksPart) is not None
    with pytest.raises(HelperPartViolation, match="a reviewer read the workers part, but its helper file does not turn on that feature"):
        readers.agent_data(reviewer).part(WorkersPart)
    assert readers.agent_data(agents.session_agent("s1")).part(WorkersPart) is not None, "the main agent reads every part"


def test_every_row_event_names_the_feature_it_belongs_to(app: App):
    from journal.events.rows.row_event import RowEvent
    from journal.events.rows.task_closed import TaskClosed
    from journal.events.rows.worker_delivered import WorkerDelivered
    from journal.features.registry import ENGINE, Registry
    registry = app.container.get(Registry)
    unknown = [kind.__name__ for kind in StateMachine.event_kinds(RowEvent) if kind is not RowEvent and kind.feature_name != ENGINE and not registry.has_feature(kind.feature_name)]
    assert not unknown, f"row events naming no feature the registry knows: {unknown}"
    assert (TaskClosed.feature_name, WorkerDelivered.feature_name) == ("tasks", "workers"), "a row event names its own feature, a worker's delivery the workers feature though it resolves a wait"


def test_a_row_event_reaches_a_helper_only_when_its_feature_is_on_the_helpers_file(app: App):
    from journal.events.rows.plan_started import PlanStarted
    from journal.events.rows.worker_mention import WorkerMention
    from journal.events.rows.worker_ready import WorkerReady
    from journal.events.rows.worker_reviewed import WorkerReviewed
    from journal.support.agent_role import AgentRole
    hook(app, "SessionStart")
    with app.container.get(Scope).environment(1):
        for session, role, state in (("rw", AgentRole.WORKER, "void"), ("rr", AgentRole.REVIEWER, "reviewing")):
            app.container.get(Agents).save(Agent(environment_id=1, session=session, provider="claude", state=state, role=role), Actor.system())
    machine, mention = app.container.get(StateMachine), WorkerMention(id=1, name="Mr. Hooke", dispatcher="s1")
    sessions = lambda event: {agent.session for agent in machine.audience(event)}
    assert sessions(PlanStarted(environment_id=1, plan_id=1, task_id=0)) == {"s1"}, "a plan's start reaches no helper, whose file turns no plans on"
    assert "rw" in sessions(WorkerReady(environment_id=1, worker=mention)), "a worker hears the workers feature's events"
    assert "rr" in sessions(WorkerReviewed(environment_id=1, worker=mention, task=1, reviewer=1, reviewer_session="rr", report="")) and "rr" not in sessions(WorkerReady(environment_id=1, worker=mention)), "a reviewer hears its review and not a worker's clock-in"


HELPER_SWEEP_EVENTS = ("a write", "a stop with a task open", "a message of the user's", "a plan started", "a task edited")


@pytest.mark.parametrize("role_name", ["worker", "reviewer", "verifier", "subagent"])
def test_each_helper_role_is_deaf_to_the_main_agents_conduct(app: App, role_name: str):
    """The events that nudge or hold the main agent, sent to one helper role: every line it gets comes from the engine or a feature its file turns on, its floor stays Void, and the main agent's count does not move."""
    from journal.engine.nudger import NUDGE
    from journal.events.agent.prompt_submitted import PromptSubmitted
    from journal.events.agent.stop import Stop
    from journal.events.agent.tool_starting import ToolStarting
    from journal.events.rows.plan_started import PlanStarted
    from journal.events.rows.task_edited import TaskEdited
    from journal.features.registry import Registry
    from journal.providers.claude import Claude
    from journal.support.agent_role import AgentRole
    role = AgentRole(role_name)
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    app.console().run(["task", "create", "the main work", "--start"], AGENT)
    registry, machine, agents, entries = app.container.get(Registry), app.container.get(StateMachine), app.container.get(Agents), app.container.get(Entries)
    helper = registry.helper(role)
    with app.container.get(Scope).environment(1):
        agents.save(Agent(environment_id=1, session="sweep", provider="claude", state=helper.first_state.name, role=role), Actor.system())
    main_uses = agents.session_agent("s1").tool_uses
    write = Claude().call("Write", {"file_path": str(app.config.root / "a.py"), "content": "x"}, frozenset())
    events = (ToolStarting(call=write), Stop(), PromptSubmitted(prompt="please look at the parser"))
    with app.container.get(Scope).environment(1):
        for event in events:
            machine.reply(agents.session_agent("sweep"), event.placed("sweep", 1, "claude", None, 1.0))
        machine.row_replies(PlanStarted(environment_id=1, plan_id=1, task_id=0))
        machine.row_replies(TaskEdited(environment_id=1, task_id=1, changes=("brief",)))
        said = [entry.data["key"] for entry in entries.kind_entries(NUDGE) if entry.data.get("session") == "sweep"]
    allowed = {"engine", *helper.feature_names()}
    assert all(key.split(".")[0] in allowed for key in said), f"{role_name} heard {HELPER_SWEEP_EVENTS} and was told lines of features its file does not turn on: {said}"
    assert app.container.get(StatesCatalogue).stack(agents.session_agent("sweep")).states[0].name == "void", "its floor stays Void"
    assert agents.session_agent("s1").tool_uses == main_uses, "and the main agent's count does not move"


def test_a_subagents_tool_use_lands_on_its_own_row_researching_and_its_end_pops_it(app: App):
    from journal.support.agent_role import AgentRole
    agents, catalogue = app.container.get(Agents), app.container.get(StatesCatalogue)
    stack = lambda session: [state.name for state in catalogue.stack(agents.session_agent(session)).states]
    hook(app, "SessionStart")
    main_before = stack("s1")
    hook(app, "SubagentStart", agent_id="sub1", agent_type="Explore")
    assert agents.session_agent("s1:sub1").role == AgentRole.SUBAGENT and stack("s1:sub1") == ["void", "researching"], "a subagent's start makes its own row, researching over Void"
    status, body = hook(app, "PreToolUse", agent_id="sub1", tool_name="Write", tool_input={"file_path": "a.py", "content": "x"})
    assert status == 200 and "[journal]" not in json.dumps(body), "its tool use is answered on its own row, with no main line"
    with app.container.get(Scope).environment(1):
        assert any(entry.data.get("session_id") == "s1:sub1" for entry in app.container.get(Entries).kind_entries("ToolStarting")), "and recorded as its own"
    assert stack("s1") == main_before, "the main agent's stack does not move"
    hook(app, "SubagentStop", agent_id="sub1", last_assistant_message="found it")
    assert stack("s1:sub1") == ["void", "ended"], "its end pops Researching back to Void and ends its row"
    hook(app, "SubagentStart", agent_id="sub2", agent_type="Explore")
    hook(app, "SessionEnd", reason="exit")
    assert stack("s1:sub2")[-1] == "ended" and not [row for row in agents.unended() if row.role == AgentRole.SUBAGENT], "a subagent left running ends with its main session, so no researcher row is left to hear row events"


def test_a_helper_with_no_job_stops_from_void_and_its_row_ends(app: App):
    from journal.support.agent_role import AgentRole
    hook(app, "SessionStart")
    agents = app.container.get(Agents)
    with app.container.get(Scope).environment(1):
        for session, role in (("hw", AgentRole.WORKER), ("hr", AgentRole.REVIEWER)):
            agents.save(Agent(environment_id=1, session=session, provider="claude", state="void", role=role), Actor.system())
    for session in ("hw", "hr"):
        assert [hook(app, "Stop", session_id=session)[1].get("decision") for _ in range(6)] == [None] * 6, f"{session}: a helper in Void stops without a hold, so it never loops on its stop"
        hook(app, "SessionEnd", session_id=session)
        assert agents.session_agent(session).stack[-1]["state"] == "ended", f"{session}: its row ends with the session"


def test_a_helper_reset_by_panic_or_swapped_keeps_void_and_its_job(app: App):
    from journal.engine.states.void import Void
    from journal.features.workers.states.working_task import WorkingTask
    from journal.support.agent_role import AgentRole
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    hook(app, "SessionStart")
    scope, workers, tasks, agents, machine = app.container.get(Scope), app.container.get(Workers), app.container.get(Tasks), app.container.get(Agents), app.container.get(StateMachine)
    with scope.environment(1):
        agents.save(Agent(environment_id=1, session="wr", provider="claude", state="void", role=AgentRole.WORKER), Actor.system())
        worker = workers.save(Worker(environment_id=1, name="Mr. Reset", brief="r", session="wr"), Actor.system())
        tasks.handover(tasks.save(Task(environment_id=1, title="the lexer", brief="b"), Actor.system()), Ref.build(worker), Actor.system())
        workers.save(workers.find(worker.id).ready(1.0), Actor.worker(worker.id))
        machine.push("wr", 1, Void(), Actor.user(1), "a state over the job")
        machine.reset("wr", 1, Actor.user(1), "journal panic idle")
    assert [layer["state"] for layer in agents.session_agent("wr").stack] == ["void", "working_task"], "a reset worker keeps Void and its job, and loses what was over it"
    swapped = machine.placed(Stack((Void(), WorkingTask(task_id=1))), Void(), AgentRole.WORKER)
    assert [type(state) for state in swapped.states] == [Void], "a swap on a helper keeps Void at the bottom, never idle"
    assert [state.name for state in machine.placed(Stack((Void(),)), WorkingTask(task_id=1), AgentRole.WORKER).states] == ["void", "working_task"]
