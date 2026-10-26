"""Who takes which task next, as doc 1068 rules it: each row of ASSIGNMENT_CASES builds a situation through the hooks and commands an agent and the user really run, plays one event and checks the outcome, the task the agent holds after it and whether its stop goes through."""

from dataclasses import dataclass, field
from typing import Callable

import pytest

from journal.app import App
from journal.engine.no_task_assigner import NoTaskAssigner
from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.assigner_resolution import AssignerResolution
from journal.features.plans.support.plan_start_task_assigner import PlanStartTaskAssigner
from journal.features.plans.support.plan_task_assigner import PlanTaskAssigner
from journal.features.workers.support.orchestrator_task_assigner import OrchestratorTaskAssigner
from journal.models.agent import Agent
from journal.support.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.test_features import booted, hook, viewer
from tests.user_settings import user_set

AGENT = Caller.agent("main", "s1", "claude")
USER = Caller.user("main")
MAIN = 1


@pytest.fixture(scope="module")
def boot():
    return booted


@pytest.fixture
def app(app: App):
    with app.container.get(Scope).environment(MAIN):
        hook(app, "SessionStart")
        app.console().run(["environment", "overview"], AGENT)
        yield app


def made(app: App, argv: list[str], caller: Caller = USER) -> int:
    output = app.console().run(argv, caller)
    assert output.code == 0, output.error
    return int(output.text.split()[1].rstrip(":"))


def opened(app: App, title: str, priority: str = "") -> int:
    return made(app, ["task", "create", title, "--brief", f"{title} is done", *(["--priority", priority] if priority else [])])


def started(app: App, title: str) -> int:
    return made(app, ["task", "create", title, "--brief", f"{title} is done", "--start"], AGENT)


def run(app: App, argv: list[str], caller: Caller = AGENT) -> None:
    output = app.console().run(argv, caller)
    assert output.code == 0, output.error


def approved(app: App, phases: list[list[str]], checkpoint_after: int = 0) -> tuple[int, list[int]]:
    plan = made(app, ["plan", "create", "the plan", "--brief", "the plan is done"])
    ids = []
    for n, titles in enumerate(phases, 1):
        run(app, ["plan", "phase", str(plan), f"phase {n}", "--when", "its tasks are done", *(["--checkpoint"] if n == checkpoint_after else [])], USER)
        phase_ids = [made(app, ["plan", "add", str(plan), title, "--brief", f"{title} is done"]) for title in titles]
        run(app, ["plan", "todos", str(plan), str(n), *map(str, phase_ids)], USER)
        ids += phase_ids
    run(app, ["plan", "ready", str(plan)], USER)
    run(app, ["plan", "approve", str(plan)], USER)
    return plan, ids


def planned(app: App, phases: list[list[str]], checkpoint_after: int = 0) -> list[int]:
    plan = made(app, ["plan", "create", "the plan", "--brief", "the plan is done"])
    ids = []
    for n, titles in enumerate(phases, 1):
        run(app, ["plan", "phase", str(plan), f"phase {n}", "--when", "its tasks are done", *(["--checkpoint"] if n == checkpoint_after else [])], USER)
        phase_ids = [made(app, ["plan", "add", str(plan), title, "--brief", f"{title} is done"]) for title in titles]
        run(app, ["plan", "todos", str(plan), str(n), *map(str, phase_ids)], USER)
        ids += phase_ids
    run(app, ["plan", "ready", str(plan)], USER)
    run(app, ["plan", "approve", str(plan)], USER)
    run(app, ["plan", "start", str(plan)])
    return ids


def agent_id(app: App) -> int:
    return app.container.get(Agents).session_agent("s1").id


@dataclass(frozen=True)
class Outcome:
    """What a row expects after its event: the task the agent holds, none when 0, and whether its stop goes through."""

    in_hand: int = 0
    stop_passes: bool | None = None


@dataclass(frozen=True)
class Case:
    """One situation: a name in plain words, how it is built, auto mode on or off, the event played and the outcome expected; the built situation hands the event the numbers of the tasks it made."""

    name: str
    auto: bool
    build: Callable[[App], dict]
    event: Callable[[App, dict], None]
    expected: Callable[[dict], Outcome]
    marks: tuple = field(default_factory=tuple)


def stop(app: App, made_rows: dict) -> None:
    made_rows["stop"] = hook(app, "Stop")[1]


def complete(name: str) -> Callable[[App, dict], None]:
    return lambda app, rows: run(app, ["task", "complete", str(rows[name]), "--how", "done"])


def two_open(app: App) -> dict:
    return {"a": opened(app, "the parser"), "b": opened(app, "the lexer")}


def one_started_one_open(app: App) -> dict:
    rows = {"a": started(app, "the parser")}
    rows["b"] = opened(app, "the lexer")
    return rows


def started_alone(app: App) -> dict:
    return {"a": started(app, "the parser")}


def plan_at_its_checkpoint(app: App) -> dict:
    first, second, third = planned(app, [["the parser", "the lexer"], ["the printer"]], checkpoint_after=1)
    run(app, ["task", "complete", str(first), "--how", "done"])
    return {"first": first, "second": second, "third": third}


def paused_by_the_user(app: App) -> dict:
    rows = {"a": started(app, "the parser")}
    viewer(app, f"agents/{agent_id(app)}/pause")
    return rows


def awaiting(app: App) -> dict:
    rows = {"a": started(app, "the parser")}
    run(app, ["await", "the build", "--until", "sleep 600"])
    return rows


def plan_task_in_hand_while_awaiting(app: App) -> dict:
    first, second = planned(app, [["the parser", "the lexer"]])
    run(app, ["await", "the build", "--until", "sleep 600"])
    return {"first": first, "second": second}


def stuck(app: App) -> dict:
    rows = {"a": started(app, "the parser")}
    run(app, ["stuck", "the parser waits on a library that does not build"])
    return rows


def compacting(app: App) -> dict:
    rows = {"a": started(app, "the parser"), "b": opened(app, "the lexer")}
    hook(app, "PreCompact")
    return rows


def by_priority(app: App) -> dict:
    return {"low": opened(app, "the parser"), "high": opened(app, "the lexer", "high")}


def own_paused_and_open(app: App) -> dict:
    rows = {"paused": started(app, "the parser")}
    run(app, ["task", "pause", str(rows["paused"]), "the lexer first"])
    rows["open"] = opened(app, "the lexer")
    return rows


def blocked_only(app: App) -> dict:
    rows = {"blocked": opened(app, "the parser")}
    run(app, ["task", "block", str(rows["blocked"]), "waits on the vendor"])
    return rows


def user_adds_a_task_mid_work(app: App) -> dict:
    rows = {"a": started(app, "the parser")}
    rows["new"] = opened(app, "the lexer")
    return rows


def held_by_a_worker_and_open(app: App) -> dict:
    rows = {"worker": opened(app, "the parser")}
    run(app, ["worker", "dispatch", "Lady Lovelace", "--task", str(rows["worker"]), "--changes", "the files of its task", "--profile", "journal-medior", "--model", "sonnet"])
    hook(app, "PreToolUse", tool_name="Write", tool_input={"file_path": str(app.config.root / "notes.md"), "content": "x"})
    rows["open"] = opened(app, "the lexer")
    return rows


def started_then_a_new_session(app: App) -> dict:
    rows = {"a": started(app, "the parser")}
    hook(app, "SessionStart", source="startup")
    run(app, ["environment", "overview"])
    return rows


def approved_plan_and_open_work(app: App) -> dict:
    rows = {"free": opened(app, "the lexer")}
    _, (rows["first"], rows["second"]) = approved(app, [["the parser", "the printer"]])
    return rows


def a_plan_running_and_another_approved(app: App) -> dict:
    running, (first,) = approved(app, [["the floors"]])
    run(app, ["plan", "start", str(running)])
    _, (later,) = approved(app, [["the walls"]])
    return {"first": first, "later": later}


def started_by_the_agent_itself(app: App) -> dict:
    rows = {"a": opened(app, "the parser"), "b": opened(app, "the lexer")}
    run(app, ["task", "start", str(rows["b"])])
    return rows


def orchestrating_with_an_approved_plan(app: App) -> dict:
    user_set(app, "workers.mode", "orchestrator")
    _, (first,) = approved(app, [["the parser"]])
    return {"first": first}


def orchestrator_starting_a_task_itself(app: App) -> dict:
    user_set(app, "workers.mode", "orchestrator")
    rows = {"a": opened(app, "the parser")}
    run(app, ["task", "start", str(rows["a"])])
    return rows


def orchestrating_with_open_work(app: App) -> dict:
    user_set(app, "workers.mode", "orchestrator")
    return {"a": opened(app, "the parser")}


ASSIGNMENT_CASES = [
    Case("off auto mode an idle agent with open tasks may stop and is handed nothing", False, two_open, stop, lambda rows: Outcome(0, True)),
    Case("in auto mode an idle agent's stop starts the first open task", True, two_open, stop, lambda rows: Outcome(rows["a"], False)),
    Case("a task in progress never lets the agent stop, auto mode off", False, started_alone, stop, lambda rows: Outcome(rows["a"], False)),
    Case("a task in progress never lets the agent stop, auto mode on", True, started_alone, stop, lambda rows: Outcome(rows["a"], False)),
    Case("in auto mode completing a task starts the next open one", True, one_started_one_open, complete("a"), lambda rows: Outcome(rows["b"])),
    Case("off auto mode completing a task starts nothing", False, one_started_one_open, complete("a"), lambda rows: Outcome(0)),
    Case("off auto mode a started plan stops at its checkpoint", False, plan_at_its_checkpoint, complete("second"), lambda rows: Outcome(0)),
    Case("in auto mode a started plan goes past its checkpoint to its end", True, plan_at_its_checkpoint, complete("second"), lambda rows: Outcome(rows["third"])),
    Case("the user's pause lets a stop through with the task still in hand", True, paused_by_the_user, stop, lambda rows: Outcome(rows["a"], True)),
    Case("a wait lets a stop through with the task still in hand", True, awaiting, stop, lambda rows: Outcome(rows["a"], True)),
    Case("a plan task closed while the agent awaits something starts the plan's next task", False, plan_task_in_hand_while_awaiting, complete("first"), lambda rows: Outcome(rows["second"])),
    Case("an agent that said it is stuck may stop with the task still in hand", True, stuck, stop, lambda rows: Outcome(rows["a"], True)),
    Case("a compaction keeps the task in hand and starts no other", True, compacting, stop, lambda rows: Outcome(rows["a"])),
    Case("in auto mode the higher priority goes first", True, by_priority, stop, lambda rows: Outcome(rows["high"], False)),
    Case("in auto mode the agent's own paused task is taken up before an open one", True, own_paused_and_open, stop, lambda rows: Outcome(rows["paused"], False)),
    Case("a blocked task is never started, so with nothing else the stop goes through", True, blocked_only, stop, lambda rows: Outcome(0, True)),
    Case("in auto mode a task the user added while the agent worked is next", True, user_adds_a_task_mid_work, complete("a"), lambda rows: Outcome(rows["new"])),
    Case("the orchestrator never starts a task on itself", True, orchestrating_with_open_work, stop, lambda rows: Outcome(0)),
    Case("off auto mode the orchestrator never starts a task on itself either", False, orchestrating_with_open_work, stop, lambda rows: Outcome(0)),
    Case("an orchestrator asked to do a task itself starts it and keeps it in hand", True, orchestrator_starting_a_task_itself, stop, lambda rows: Outcome(rows["a"])),
    Case("the orchestrator's stop opens an approved plan for the workers and starts none of its tasks on itself", True, orchestrating_with_an_approved_plan, stop, lambda rows: Outcome(0)),
    Case("a task a worker holds is never started on the main agent", True, held_by_a_worker_and_open, stop, lambda rows: Outcome(rows["open"], False)),
    Case("a new session keeps the task in hand and its stop is refused", False, started_then_a_new_session, stop, lambda rows: Outcome(rows["a"], False)),
    Case("at a stop an approved plan waiting is started, its first task in hand, never a free task beside it", True, approved_plan_and_open_work, stop, lambda rows: Outcome(rows["first"], False)),
    Case("a task the agent started itself is the one in hand, and its stop starts no second", True, started_by_the_agent_itself, stop, lambda rows: Outcome(rows["b"], False)),
    Case("while a plan runs, a stop goes on with its task and never starts or names another approved plan", True, a_plan_running_and_another_approved, stop, lambda rows: Outcome(rows["first"], False)),
]


@pytest.mark.parametrize("case", ASSIGNMENT_CASES, ids=[case.name for case in ASSIGNMENT_CASES])
def test_who_takes_which_task_next(app: App, case: Case):
    user_set(app, "tasks.auto", case.auto)
    rows = case.build(app)
    case.event(app, rows)
    app.runtime().deferred.drain()
    expected = case.expected(rows)
    in_hand = [task.id for task in app.container.get(Tasks).agent_started()]
    assert in_hand == ([expected.in_hand] if expected.in_hand else []), f"{case.name}: the agent holds {in_hand or 'nothing'}"
    if expected.stop_passes is not None:
        assert (rows["stop"].get("decision") != "block") == expected.stop_passes, f"{case.name}: the stop answered {rows['stop']}"


RESOLUTION_CASES = [
    (AgentRole.MAIN, (), PlanStartTaskAssigner),
    (AgentRole.MAIN, ("idle",), PlanStartTaskAssigner),
    (AgentRole.MAIN, ("idle", "working"), PlanStartTaskAssigner),
    (AgentRole.MAIN, ("soloing", "working"), PlanStartTaskAssigner),
    (AgentRole.MAIN, ("idle", "working", "sorting_dump"), PlanStartTaskAssigner),
    (AgentRole.MAIN, ("orchestrating",), OrchestratorTaskAssigner),
    (AgentRole.MAIN, ("idle", "following_plan"), PlanTaskAssigner),
    (AgentRole.MAIN, ("idle", "working", "paused"), NoTaskAssigner),
    (AgentRole.MAIN, ("idle", "working", "awaiting"), PlanStartTaskAssigner),
    (AgentRole.MAIN, ("idle", "following_plan", "awaiting"), PlanTaskAssigner),
    (AgentRole.MAIN, ("idle", "working", "stuck"), NoTaskAssigner),
    (AgentRole.MAIN, ("idle", "working", "waiting"), NoTaskAssigner),
    (AgentRole.MAIN, ("idle", "working", "compacting"), NoTaskAssigner),
    (AgentRole.MAIN, ("idle", "reading_overview"), NoTaskAssigner),
    (AgentRole.MAIN, ("idle", "demand_block"), PlanStartTaskAssigner),
    (AgentRole.MAIN, ("idle", "panicking"), NoTaskAssigner),
    (AgentRole.MAIN, ("ended",), NoTaskAssigner),
    (AgentRole.WORKER, ("void", "working_task"), NoTaskAssigner),
    (AgentRole.WORKER, ("working_task",), NoTaskAssigner),
    (AgentRole.REVIEWER, ("reviewing",), NoTaskAssigner),
    (AgentRole.VERIFIER, ("verifying",), NoTaskAssigner),
    (AgentRole.SUBAGENT, ("researching",), NoTaskAssigner),
]


@pytest.mark.parametrize("role, stack, expected", RESOLUTION_CASES, ids=["/".join((role.value, *stack)) for role, stack, _ in RESOLUTION_CASES])
def test_the_state_closest_to_the_top_that_names_an_assigner_decides(app: App, role: AgentRole, stack: tuple, expected: type):
    agent = Agent(environment_id=MAIN, session="s9", provider="claude", role=role, stack=tuple({"state": name, "data": {}} for name in stack))
    assert type(app.container.get(AssignerResolution).resolved(agent)) is expected


def test_every_floor_names_an_assigner(app: App):
    catalogue = app.container.get(StatesCatalogue)
    floors = [catalogue.first(), *(state() for state in catalogue.role_floors.values()), *(state() for modes in catalogue.modes for state in modes.states.values())]
    assert [type(state).__name__ for state in floors if state.assigner is None] == []


def test_the_orchestrators_next_task_is_one_it_hands_a_worker_in_turn_across_its_plans_and_never_starts(app: App):
    from journal.events.agent.stop import Stop
    user_set(app, "workers.mode", "orchestrator")
    user_set(app, "tasks.auto", True)
    first_plan, (floors,) = approved(app, [["the floors"]])
    run(app, ["plan", "start", str(first_plan)])
    second_plan, (walls,) = approved(app, [["the walls"]])
    run(app, ["plan", "start", str(second_plan)])
    agent = app.container.get(Agents).session_agent("s1")
    assignment = app.container.get(OrchestratorTaskAssigner).next_task(agent, Stop(session="s1", environment_id=MAIN))
    assert assignment.task_id in (floors, walls) and "hand a worker" in assignment.reason, assignment
    assert app.container.get(Tasks).agent_started() == [], "the orchestrator starts none of them on itself"


def worker_through_its_task(app: App, queued: bool) -> dict:
    from journal.repositories.workers import Workers
    rows = {"first": opened(app, "the parser"), "second": opened(app, "the lexer")}
    run(app, ["worker", "dispatch", "Lady Lovelace", "--task", str(rows["first"]), "--changes", "the files of its task", "--profile", "journal-medior", "--model", "sonnet"])
    if queued:
        run(app, ["worker", "queue", "1", str(rows["second"])])
    workers = app.container.get(Workers)
    workers.save(workers.find(1).with_(token_hash="h", session="w-1", resume="w-1").ready(1.0), Actor.system())
    lovelace = Caller.worker("main", 1, "w-1", "claude")
    run(app, ["proof", "1", "parser.py:3, test_reads_the_grammar passes"], lovelace)
    run(app, ["clock-out", "the parser reads the grammar"], lovelace)
    app.runtime().deferred.drain()
    return rows


def test_a_worker_goes_on_to_its_queued_task_and_the_main_agent_takes_none_of_its_tasks(app: App):
    rows = worker_through_its_task(app, queued=True)
    tasks = app.container.get(Tasks)
    assert tasks.find(rows["second"]).delegated, "the queued task is the worker's, handed on by the worker actions"
    assert tasks.agent_started() == [], "the main agent is started on none of the worker's tasks"


def test_a_worker_with_an_empty_queue_is_handed_nothing_more(app: App):
    rows = worker_through_its_task(app, queued=False)
    tasks = app.container.get(Tasks)
    assert not tasks.find(rows["second"]).delegated and tasks.agent_started() == [], "an empty queue hands the worker nothing, and the main agent takes nothing of it"


def test_asked_for_three_the_orchestrators_assigner_names_three_tasks_in_turn_and_starts_none(app: App):
    from journal.events.agent.stop import Stop
    user_set(app, "workers.mode", "orchestrator")
    user_set(app, "tasks.auto", True)
    plan_tasks = []
    for title in ("the floors", "the walls", "the roof"):
        plan, ids = approved(app, [[f"{title} one", f"{title} two"]])
        run(app, ["plan", "start", str(plan)])
        plan_tasks.append(ids)
    agent = app.container.get(Agents).session_agent("s1")
    assignment = app.container.get(OrchestratorTaskAssigner).next_task(agent, Stop(session="s1", environment_id=MAIN), quantity=3)
    assert len(set(assignment.task_ids())) == 3 and {plan_tasks[n][0] for n in range(3)} == set(assignment.task_ids()), assignment
    assert app.container.get(Tasks).agent_started() == [], "naming three starts none on the orchestrator"


def test_asked_for_three_the_builders_assigner_starts_the_first_and_names_the_two_after_it(app: App):
    from journal.events.agent.stop import Stop
    user_set(app, "tasks.auto", True)
    first, second, third = (opened(app, title) for title in ("the parser", "the lexer", "the printer"))
    agent = app.container.get(Agents).session_agent("s1")
    assignment = app.container.get(PlanStartTaskAssigner).next_task(agent, Stop(session="s1", environment_id=MAIN), quantity=3)
    assert assignment.task_ids() == (first, second, third), assignment
    assert [task.id for task in app.container.get(Tasks).agent_started()] == [first], "only the first is started, one task in hand at a time"
