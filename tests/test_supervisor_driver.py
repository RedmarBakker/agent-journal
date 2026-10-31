import array
import json
import os
import socket
import threading
from uuid import uuid4

import pytest

from journal.app import App
from journal.config import Config
from journal.engine.agent_launcher import AgentLauncher
from journal.events.announcer import Announcer
from journal.events.rows.plan_work_available import PlanWorkAvailable
from journal.features.plans.plans_options import PlansOptions
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.supervisor.support.supervisor_maintenance import diagnostic_task_values
from journal.features.supervisor.support.supervisor_work_available import SupervisorWorkAvailable
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.check import Check
from journal.models.entry import Entry
from journal.models.link import Link
from journal.models.phase import Phase
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.template import Template
from journal.repositories.agents import Agents
from journal.repositories.checks import Checks
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.repositories.links import Links
from journal.repositories.phases import PHASE_TASK_LINK, Phases
from journal.repositories.plans import PHASE_LINK, Plans
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.tasks import PLAN_LINK, Tasks
from journal.repositories.templates import Templates
from journal.support.actor import Actor
from journal.support.caller import Caller
from journal.support.time_source import TimeSource
from journal.support.rejection import Rejection
from journal.supervisor_link import SupervisorLink
from journal.supervisor_authority import SUPERVISOR_ACTOR, SupervisorAuthority
from journal.features.plans.support.plan_agents import PlanAgents
from tests.in_process import posted
from tests.test_features import booted
from tests.test_supervisor_actions import _admitted_maintenance_context, diagnostic_operation, maintenance_request
from tests.test_supervisor_authority import Fixture, enrollment
from tests.user_settings import user_set

MAIN = 1


def test_plan_launcher_uses_the_persistent_codex_home_only_for_plan_environments(monkeypatch, tmp_path):
    monkeypatch.setenv("JOURNAL_CODEX_HOME", "/var/lib/journal-codex")
    monkeypatch.setenv("CODEX_HOME", "/data/home/.codex")
    launcher = AgentLauncher(Config(tmp_path))

    plan = launcher.launch_environment("plan-12", "8421")
    task = launcher.launch_environment("task-12", "8421")

    assert plan["CODEX_HOME"] == "/var/lib/journal-codex"
    assert "CODEX_HOME" not in task


def test_restricted_plan_launcher_sends_only_the_fixed_driver_request(monkeypatch, tmp_path):
    socket_path = tmp_path / "plan-driver.sock"
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(socket_path))
    server.listen(1)
    received = []

    def accept_request():
        connection, _ = server.accept()
        with connection:
            data, ancillary, _, _ = connection.recvmsg(65536, socket.CMSG_SPACE(array.array("i").itemsize))
            received.append(json.loads(data))
            for level, kind, payload in ancillary:
                if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                    descriptor = array.array("i")
                    descriptor.frombytes(payload[:array.array("i").itemsize])
                    for item in descriptor:
                        os.close(item)
            connection.sendall(b'{"pid":4321}')

    listener = threading.Thread(target=accept_request)
    listener.start()
    monkeypatch.setenv("JOURNAL_PLAN_DRIVER_SOCKET", str(socket_path))
    launcher = AgentLauncher(Config(tmp_path))
    monkeypatch.setattr(launcher, "plan_worktree_permissions", lambda _worktree: None)
    worktree = tmp_path / ".claude" / "worktrees" / "plan-12"
    arguments = ["codex", "--env", "plan-12", "--worktree", "plan-12", "--yes", "--no-open", "--no-journal", "--skip", "--", "--resume", "session-12"]

    pid = launcher.launched("plan-12", arguments, worktree)

    listener.join(timeout=2)
    server.close()
    assert not listener.is_alive()
    assert pid == 4321
    assert received == [{
        "environment": "plan-12",
        "root": str(tmp_path.resolve()),
        "worktree": str(worktree.resolve()),
        "port": "8421",
        "resume": ["--resume", "session-12"],
    }]


@pytest.fixture(scope="module")
def boot():
    return booted


class DriverProcesses:
    def __init__(self, app: App) -> None:
        self.app = app
        self.running: set[int] = set()

    def start(self, environment: str, _agent: str, _resume: tuple[str, ...]) -> int:
        self.running.add(self.app.container.get(Environments).existing(environment).row_id)
        return 1

    def stop(self, environment_id: int) -> None:
        self.running.discard(environment_id)


def prepare_driver_processes(app: App, monkeypatch) -> DriverProcesses:
    processes = DriverProcesses(app)
    monkeypatch.setattr(AgentLauncher, "start_in_worktree", lambda _self, environment, agent, resume, repositories=None: processes.start(environment, agent, resume))
    monkeypatch.setattr(SupervisorLink, "runs", lambda _self, environment_id: environment_id in processes.running)
    monkeypatch.setattr(SupervisorLink, "stop", lambda _self, environment_id: processes.stop(environment_id))
    monkeypatch.setattr(SupervisorLink, "type", lambda *_args, **_kwargs: None)
    return processes


@pytest.fixture
def driver_processes(app: App, monkeypatch) -> DriverProcesses:
    return prepare_driver_processes(app, monkeypatch)


def start_normal_driver(app: App, driver_processes: DriverProcesses) -> Fixture:
    user_set(app, OrganizationOptions.PLAN_MODE.key, "solo")
    user_set(app, PlansOptions.PLAN_AGENTS.key, True)
    status, answer = posted(app, "/hooks/codex", {"hook_event_name": "SessionStart", "session_id": "supervisor-main"}, {"X-Journal-Env": "main"})
    assert status < 400, answer
    app.runtime().deferred.drain()

    actor = Caller.user("main").actor
    scope = app.container.get(Scope)
    plans, phases, links = app.container.get(Plans), app.container.get(Phases), app.container.get(Links)
    environments = app.container.get(Environments)
    time_source = app.container.get(TimeSource)
    with scope.environment(MAIN):
        owner_environment = environments.find(MAIN)
        plan = plans.save(Plan(environment_id=MAIN, title="managed diagnostic plan", brief="Complete the current work"), actor)
        phase = phases.save(Phase(environment_id=MAIN, title="current phase", completion_rule="the open work is complete"), actor)
        links.save(Link(source=Ref.build(phase), target=Ref.build(plan), link_type=PHASE_TASK_LINK), actor)
        plan = plans.save(plan.user_approved(time_source.seconds()), actor)
        plan = plans.start(plan, None, actor)
    app.runtime().deferred.drain()

    plan_agents = app.container.get(PlanAgents)
    with scope.environment(MAIN):
        plan = plans.find(plan.row_id)
        driver_environment = plan_agents.environment(plan)
        driver_agent_id = plans.agent_id(plan)
    assert driver_environment is not None and driver_environment.name == f"plan-{plan.id}"
    status, answer = posted(app, "/hooks/codex", {"hook_event_name": "SessionStart", "session_id": f"plan-driver-{plan.id}"}, {"X-Journal-Env": driver_environment.name})
    assert status < 400, answer
    app.runtime().deferred.drain()

    with scope.environment(MAIN):
        template = app.container.get(Templates).save(Template(title=f"diagnostic-{uuid4().hex}", purpose="diagnose the failed service check", brief="read only", targets=("plan",)), Actor.system())
        check = app.container.get(Checks).save(Check(title="health check", brief="Read-only health check", command="true", interval=10), actor)
    with scope.environment(driver_environment.row_id):
        agent = app.container.get(Agents).find(driver_agent_id)
    fixture = Fixture(app.container.get(SupervisorAuthority), actor, owner_environment, driver_environment, plan, phase, Task(), agent, check, template)
    return fixture


def stop_normal_driver(fixture: Fixture) -> None:
    fixture.authority.secrets_store.drop(fixture.credentials)


@pytest.fixture
def normal_driver(app: App, driver_processes: DriverProcesses) -> Fixture:
    fixture = start_normal_driver(app, driver_processes)
    yield fixture
    stop_normal_driver(fixture)


def add_phase_task(app: App, fixture: Fixture, title: str, brief: str) -> Task:
    with app.container.get(Scope).environment(fixture.owner_environment.row_id):
        task = app.container.get(Tasks).save(Task(environment_id=fixture.owner_environment.row_id, title=title, brief=brief), fixture.owner)
        app.container.get(Plans).place_task_in_phase(task, fixture.plan, fixture.phase, fixture.owner)
        fixture.task = task
        return task


def action_context(app: App, monkeypatch, fixture: Fixture):
    context = _admitted_maintenance_context(app, monkeypatch, fixture, "bounded_write")
    context["driver_session"] = fixture.agent.session
    return context


def work_delivery(app: App, scope: Scope, receipt_id: int):
    with scope.environment(PROJECT):
        rows = app.container.get(Entries).supervisor_records("SupervisorActionDelivery", last=100, receipt_id=receipt_id)
    return rows[-1] if rows else None


def test_idle_normal_driver_takes_current_phase_diagnostic_without_owner_prompt(app: App, normal_driver: Fixture, monkeypatch, driver_processes: DriverProcesses):
    fixture = normal_driver
    title, brief = diagnostic_task_values(fixture.template)
    diagnostic = add_phase_task(app, fixture, title, brief)
    context = action_context(app, monkeypatch, fixture)
    request = maintenance_request(context, [diagnostic_operation(context)])
    announced = []
    original_announce = Announcer.announce

    def capture(announcer, event):
        announced.append(event)
        return original_announce(announcer, event)

    monkeypatch.setattr(Announcer, "announce", capture)

    receipt = context["maintenance"].apply_maintenance(context["principal"], request)

    agent = app.container.get(Agents).unended_agent(fixture.agent.row_id)
    with context["scope"].environment(fixture.owner_environment.row_id):
        task = app.container.get(Tasks).find(diagnostic.row_id)
    with context["scope"].environment(fixture.driver_environment.row_id):
        holder = app.container.get(Tasks).task_holder(task.row_id)
    assert receipt["status"] == "applied" and receipt["data"]["verification"] == "verified", "the committed maintenance receipt admits its diagnostic"
    assert fixture.agent.environment_id in driver_processes.running and agent.provider == "codex" and agent.session == f"plan-driver-{fixture.plan.id}", "the ordinary bound Plan agent is running through its Codex session"
    assert [(layer["state"], layer["data"].get("plan_id")) for layer in agent.stack] == [("leading_plan", fixture.plan.row_id), ("following_plan", fixture.plan.row_id)], "the driver is following its bound plan through the normal state machine"
    assert task.state == TaskState.STARTED and holder == Ref.build(agent), "the normal row-event assignment path starts the eligible current-phase diagnostic in the bound driver"
    assert len(announced) == 1 and isinstance(announced[0], PlanWorkAvailable) and announced[0].environment_id == fixture.agent.environment_id and announced[0].plan_id == fixture.plan.row_id, "the committed receipt signals work in its bound Plan environment"
    assert work_delivery(app, context["scope"], receipt["receipt_id"]).data["status"] == "notified", "the action receipt has a separate work-delivery record"


def test_live_codex_plan_grant_stays_within_the_smoke_token_and_request_caps(app: App, normal_driver: Fixture):
    fixture = normal_driver
    add_phase_task(app, fixture, "bounded smoke driver", "Keep one eligible task open for the bounded staging grant")
    request = enrollment(fixture, "bounded_write")
    request["limits"].update({
        "max_turns_per_day": 1,
        "max_input_tokens_per_turn": 24000,
        "max_output_tokens_per_turn": 8000,
        "max_provider_requests_per_turn": 8,
        "max_turn_seconds": 600,
        "max_cost_microusd_per_day": 1000000,
    })

    grant, _token = fixture.authority.enroll(fixture.owner, request)
    fixture.credentials.append(fixture.authority._credential_name(grant["grant_id"], grant["grant_version"]))

    assert grant["driver_provider"] == "codex" and grant["driver_agent_id"] == fixture.agent.row_id
    assert grant["limits"]["max_input_tokens_per_turn"] == 24000
    assert grant["limits"]["max_output_tokens_per_turn"] == 8000
    assert grant["limits"]["max_provider_requests_per_turn"] == 8
    assert grant["limits"]["max_turns_per_day"] == 1
    assert grant["limits"]["max_cost_microusd_per_day"] == 1000000


def test_busy_driver_keeps_task_then_takes_eligible_diagnostic(app: App, normal_driver: Fixture, monkeypatch):
    fixture = normal_driver
    first = add_phase_task(app, fixture, "current task", "Finish the current work")
    status, answer = posted(app, "/hooks/codex", {"hook_event_name": "Stop", "session_id": fixture.agent.session}, {"X-Journal-Env": fixture.driver_environment.name})
    assert status < 400, answer
    agent = app.container.get(Agents).unended_agent(fixture.agent.row_id)
    with app.container.get(Scope).environment(fixture.driver_environment.row_id):
        first_holder = app.container.get(Tasks).task_holder(first.row_id)
    assert first_holder == Ref.build(agent), "the normal stop hook puts the first task in the driver's hand"
    context = action_context(app, monkeypatch, fixture)

    receipt = context["maintenance"].apply_maintenance(context["principal"], maintenance_request(context, [diagnostic_operation(context)]))
    with context["scope"].environment(fixture.owner_environment.row_id):
        title, brief = diagnostic_task_values(fixture.template)
        diagnostic = next(task for task in context["maintenance"].plans.phase_tasks(fixture.phase) if task.title == title and task.brief == brief)
    with context["scope"].environment(fixture.driver_environment.row_id):
        first_holder = app.container.get(Tasks).task_holder(first.row_id)
        diagnostic_holder = app.container.get(Tasks).task_holder(diagnostic.row_id)
    assert receipt["status"] == "applied" and first_holder == Ref.build(agent), "work notification leaves the current task in hand"
    assert diagnostic.state == TaskState.OPEN and diagnostic_holder is None, "a busy driver does not take another task early"

    with context["scope"].environment(fixture.owner_environment.row_id):
        current = context["maintenance"].tasks.find(first.row_id)
        context["maintenance"].tasks.save(current.completed(context["time_source"].moment(), "current work completed"), Actor.agent(agent.session))

    with context["scope"].environment(fixture.owner_environment.row_id):
        diagnostic = app.container.get(Tasks).find(diagnostic.row_id)
    with context["scope"].environment(fixture.driver_environment.row_id):
        diagnostic_holder = app.container.get(Tasks).task_holder(diagnostic.row_id)
    agent = app.container.get(Agents).unended_agent(fixture.agent.row_id)
    assert diagnostic.state == TaskState.STARTED and diagnostic_holder == Ref.build(agent), "the ordinary task-close route takes the diagnostic at the next legitimate free moment"


def test_checkpoint_waits_for_owner_even_when_tasks_auto_is_on(app: App, normal_driver: Fixture):
    fixture = normal_driver
    user_set(app, TasksOptions.AUTO.key, False)
    first = add_phase_task(app, fixture, "checkpoint work", "Finish before the owner checkpoint")
    scope = app.container.get(Scope)
    phases, links, tasks = app.container.get(Phases), app.container.get(Links), app.container.get(Tasks)
    plans = app.container.get(Plans)
    with scope.environment(fixture.owner_environment.row_id):
        fixture.phase = phases.save(fixture.phase.with_(checkpoint=True), fixture.owner)
        next_phase = phases.save(Phase(environment_id=fixture.owner_environment.row_id, title="owner review", completion_rule="the owner approves the next phase"), fixture.owner)
        links.save(Link(source=Ref.build(next_phase), target=Ref.build(fixture.plan), link_type=PHASE_TASK_LINK), fixture.owner)
        next_task = tasks.save(Task(environment_id=fixture.owner_environment.row_id, title="after checkpoint", brief="Continue after owner review"), fixture.owner)
        plans.place_task_in_phase(next_task, fixture.plan, next_phase, fixture.owner)
    status, answer = posted(app, "/hooks/codex", {"hook_event_name": "Stop", "session_id": fixture.agent.session}, {"X-Journal-Env": fixture.driver_environment.name})
    assert status < 400, answer
    agent = app.container.get(Agents).unended_agent(fixture.agent.row_id)
    with scope.environment(fixture.driver_environment.row_id):
        assert tasks.task_holder(first.row_id) == Ref.build(agent), "the normal driver starts the current phase through its hook"

    with scope.environment(fixture.owner_environment.row_id):
        current = tasks.find(first.row_id)
        tasks.save(current.completed(app.container.get(TimeSource).moment(), "checkpoint phase completed"), Actor.agent(agent.session))

    user_set(app, TasksOptions.AUTO.key, True)
    agent = app.container.get(Agents).unended_agent(fixture.agent.row_id)
    event = PlanWorkAvailable(
        environment_id=fixture.driver_environment.row_id,
        time=app.container.get(TimeSource).seconds(),
        row_id=next_task.row_id,
        actor=Actor.plugin(SUPERVISOR_ACTOR).stamp,
        plan_id=fixture.plan.row_id,
        phase_id=next_phase.row_id,
        task_id=next_task.row_id,
        receipt_id=1,
    )
    with scope.environment(fixture.driver_environment.row_id):
        app.container.get(Announcer).announce(event)

    with scope.environment(fixture.owner_environment.row_id):
        first, next_task = tasks.find(first.row_id), tasks.find(next_task.row_id)
        current_plan = plans.find(fixture.plan.row_id)
    agent = app.container.get(Agents).unended_agent(fixture.agent.row_id)
    with scope.environment(fixture.driver_environment.row_id):
        next_holder = tasks.task_holder(next_task.row_id)
    assert first.state == TaskState.COMPLETED and next_task.state == TaskState.OPEN and next_holder is None, "a supervisor work signal does not start later-phase work across the owner checkpoint"
    assert agent.stack[-1]["data"].get("checkpoint_pause") is True and current_plan.is_started(), "the plan remains at its owner checkpoint after auto mode is enabled"


@pytest.mark.parametrize("gate", ("future_phase", "owner_pause", "checkpoint", "failed_phase_tests"))
def test_future_phase_pause_checkpoint_and_failed_phase_gate_do_not_advance(app: App, normal_driver: Fixture, monkeypatch, gate: str):
    fixture = normal_driver
    task = add_phase_task(app, fixture, "current work", "Keep an open task for enrollment")
    scope = app.container.get(Scope)
    plans, phases, links, tasks = app.container.get(Plans), app.container.get(Phases), app.container.get(Links), app.container.get(Tasks)
    next_phase = None
    if gate in ("future_phase", "checkpoint"):
        with scope.environment(fixture.owner_environment.row_id):
            next_phase = phases.save(Phase(environment_id=fixture.owner_environment.row_id, title="later phase", completion_rule="later work is complete", checkpoint=gate == "checkpoint"), fixture.owner)
            links.save(Link(source=Ref.build(next_phase), target=Ref.build(fixture.plan), link_type=PHASE_TASK_LINK), fixture.owner)
            later = tasks.save(Task(environment_id=fixture.owner_environment.row_id, title="later work", brief="Work in the later phase"), fixture.owner)
            links.save(Link(source=Ref.build(later), target=Ref.build(next_phase), link_type=PHASE_LINK), fixture.owner)
            links.save(Link(source=Ref.build(later), target=Ref.build(fixture.plan), link_type=PLAN_LINK), fixture.owner)
    context = action_context(app, monkeypatch, fixture)
    request = maintenance_request(context, [diagnostic_operation(context)])
    authority = fixture.authority
    original = authority.action_context
    authority_type = type(authority)
    count = 0

    def recheck(_authority, principal):
        nonlocal count
        count += 1
        if count == 2:
            if gate == "owner_pause":
                with scope.environment(fixture.owner_environment.row_id):
                    plan = plans.find(fixture.plan.row_id)
                    plans.save(plan.user_postponed(context["time_source"].seconds()), fixture.owner)
            elif gate in ("future_phase", "checkpoint"):
                with scope.environment(fixture.owner_environment.row_id):
                    for phase_task in plans.phase_tasks(fixture.phase):
                        current = tasks.find(phase_task.row_id)
                        tasks.save(current.with_(state=TaskState.COMPLETED, completed_at=context["time_source"].moment(), outcome="fixture completed"), Actor.system())
            elif gate == "failed_phase_tests":
                monkeypatch.setattr(type(authority.phase_testing), "unpassed", lambda _testing, _plan: ("pytest",))
        return original(principal)

    monkeypatch.setattr(authority_type, "action_context", recheck)
    receipt = context["maintenance"].apply_maintenance(context["principal"], request)

    delivery = work_delivery(app, scope, receipt["receipt_id"])
    title, brief = diagnostic_task_values(fixture.template)
    with scope.environment(fixture.owner_environment.row_id):
        diagnostic = next(task for task in plans.phase_tasks(fixture.phase) if task.title == title and task.brief == brief)
    agent = app.container.get(Agents).unended_agent(fixture.agent.row_id)
    expected_reason = {
        "future_phase": "grant_context_changed",
        "owner_pause": "plan_ineligible",
        "checkpoint": "grant_context_changed",
        "failed_phase_tests": "plan_ineligible",
    }[gate]
    assert receipt["status"] == "applied" and delivery is not None and delivery.data["status"] == "needs_owner" and delivery.data["reason"] == expected_reason, "post-commit revalidation records an owner handoff when a plan gate changes"
    with scope.environment(fixture.driver_environment.row_id):
        assert tasks.task_holder(diagnostic.row_id) is None, "a changed phase, owner pause, checkpoint, or failed phase test does not assign its diagnostic to the driver"
    assert diagnostic.state != TaskState.STARTED, "the ineligible diagnostic is never started by the bound driver"
    if gate == "future_phase":
        assert authority.action_context(context["principal"])[1]["conflict_reason"] == "grant_context_changed", "a diagnostic from the old phase cannot cross into future-phase work"
    if next_phase is not None:
        with scope.environment(fixture.owner_environment.row_id):
            assert plans.find(fixture.plan.row_id).is_started(), "a phase handoff remains an owner decision"


@pytest.mark.parametrize("driver_change", ("unavailable", "incompatible"))
def test_unavailable_or_incompatible_driver_requires_owner_evidence(app: App, normal_driver: Fixture, monkeypatch, driver_change: str):
    fixture = normal_driver
    title, brief = diagnostic_task_values(fixture.template)
    add_phase_task(app, fixture, title, brief)
    context = action_context(app, monkeypatch, fixture)
    request = maintenance_request(context, [diagnostic_operation(context)])
    authority, original = fixture.authority, fixture.authority.action_context
    count = 0

    def recheck(_authority, principal):
        nonlocal count
        count += 1
        if count == 2:
            if driver_change == "unavailable":
                monkeypatch.setattr(type(authority.agents), "is_running", lambda _self, _environment: False)
            else:
                agents = app.container.get(Agents)
                with context["scope"].environment(fixture.driver_environment.row_id):
                    agent = agents.find(fixture.agent.row_id)
                    agents.save(agent.with_(provider="claude"), Actor.system())
        return original(principal)

    monkeypatch.setattr(type(authority), "action_context", recheck)
    receipt = context["maintenance"].apply_maintenance(context["principal"], request)
    delivery = work_delivery(app, context["scope"], receipt["receipt_id"])

    assert receipt["status"] == "applied" and delivery is not None and delivery.data["status"] == "needs_owner", "a driver that stopped or changed provider produces owner evidence instead of another executor"
    with context["scope"].environment(fixture.driver_environment.row_id):
        assert app.container.get(Tasks).task_holder(context["fixture"].task.row_id) is None, "unavailable or incompatible drivers do not receive diagnostic work"


def test_replayed_work_signal_does_not_reassign_or_duplicate(app: App, normal_driver: Fixture, monkeypatch):
    fixture = normal_driver
    title, brief = diagnostic_task_values(fixture.template)
    diagnostic = add_phase_task(app, fixture, title, brief)
    context = action_context(app, monkeypatch, fixture)
    request = maintenance_request(context, [diagnostic_operation(context)])
    announced = []
    original_announce = Announcer.announce

    def capture(announcer, event):
        if isinstance(event, PlanWorkAvailable):
            announced.append(event)
        return original_announce(announcer, event)

    monkeypatch.setattr(Announcer, "announce", capture)
    receipt = context["maintenance"].apply_maintenance(context["principal"], request)
    tasks, agents = app.container.get(Tasks), app.container.get(Agents)
    agent = agents.unended_agent(fixture.agent.row_id)
    with context["scope"].environment(fixture.owner_environment.row_id):
        started = tasks.find(diagnostic.row_id)
    with context["scope"].environment(fixture.driver_environment.row_id):
        holder = tasks.task_holder(started.row_id)
    started_at = started.started_at

    app.container.get(SupervisorWorkAvailable).notify(context["principal"], receipt, diagnostic.row_id)

    with context["scope"].environment(fixture.owner_environment.row_id):
        replayed = tasks.find(diagnostic.row_id)
    with context["scope"].environment(fixture.driver_environment.row_id):
        replayed_holder = tasks.task_holder(replayed.row_id)
    with context["scope"].environment(PROJECT):
        deliveries = app.container.get(Entries).supervisor_records("SupervisorActionDelivery", last=100, receipt_id=receipt["receipt_id"])
    assert holder == Ref.build(agent) == replayed_holder, "a repeated work signal leaves the canonical holder unchanged"
    assert replayed.state == TaskState.STARTED and replayed.started_at == started_at and len(deliveries) == 1 and len(announced) == 1, "a repeated work signal does not start the diagnostic again or duplicate delivery evidence"


def test_generic_entry_writes_cannot_forge_supervisor_delivery_evidence(app: App):
    with app.container.get(Scope).environment(PROJECT):
        with pytest.raises(Rejection):
            app.container.get(Entries).recorded(Entry(environment_id=PROJECT, entry_type="SupervisorActionDelivery", actor=Actor.system(), data={}, idempotency="forged-delivery"), Actor.system())
