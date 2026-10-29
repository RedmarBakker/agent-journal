"""Plan agents: with the switch on, a started plan runs in its own environment plan-<n> with its own agent and chat, started at the plan's start and stopped at its pause or end."""

import pytest

from journal.app import App
from journal.engine.agent_launcher import AgentLauncher
from journal.http.plans.plan_outline import PlanOutline
from journal.models.plan_state import PlanState
from journal.repositories.agents import Agents
from journal.repositories.entries import NUDGE, Entries
from journal.repositories.environments import Environments
from journal.repositories.messages import Messages
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.caller import Caller
from journal.supervisor_link import SupervisorLink
from tests.in_process import posted
from tests.test_features import booted, hook
from tests.user_settings import user_set

AGENT = Caller.agent("main", "s1", "claude")
USER = Caller.user("main")
MAIN = 1
SWITCH = "plans.plan_agents"


@pytest.fixture(scope="module")
def boot():
    return booted


class Supervisors:
    """The launches and stops the journal asked for, and the environments whose agent runs, in place of real processes; lines typed to them go nowhere."""

    def __init__(self) -> None:
        self.launches: list[tuple[str, str, tuple[str, ...]]] = []
        self.stops: list[int] = []
        self.running: set[str] = set()

    def launched(self, environment: str, agent: str, resume: tuple[str, ...]) -> int:
        self.launches.append((environment, agent, resume))
        self.running.add(environment)
        return 1


@pytest.fixture
def supervisors(app: App, monkeypatch) -> Supervisors:
    recorded = Supervisors()
    environments = app.container.get(Environments)
    monkeypatch.setattr(AgentLauncher, "start_in_worktree", lambda self, environment, agent, resume: recorded.launched(environment, agent, resume))
    monkeypatch.setattr(SupervisorLink, "runs", lambda self, environment_id: environments.find(environment_id).name in recorded.running)

    def stopped(self, environment_id: int) -> None:
        recorded.stops.append(environment_id)
        recorded.running.discard(environments.find(environment_id).name)

    monkeypatch.setattr(SupervisorLink, "stop", stopped)
    monkeypatch.setattr(SupervisorLink, "type", lambda self, environment_id, line, following=0.0: None)
    monkeypatch.setattr(SupervisorLink, "type_whole", lambda self, environment_id, flagged, following: None)
    return recorded


@pytest.fixture
def app(app: App):
    with app.container.get(Scope).environment(MAIN):
        hook(app, "SessionStart")
        app.console().run(["environment", "overview"], AGENT)
        yield app


def started_plan(app: App, title: str) -> int:
    console = app.console()
    plan = int(console.run(["plan", "create", title, "--brief", f"{title} done"], USER).text.split()[1].rstrip(":"))
    console.run(["plan", "add", str(plan), f"the first step of {title}"], USER)
    assert console.run(["plan", "approve", str(plan)], USER).code == 0
    output = console.run(["plan", "start", str(plan)], USER)
    assert output.code == 0, output.error
    app.runtime().deferred.drain()
    return plan


def plan_environment(app: App, plan: int):
    return app.container.get(Environments).existing(f"plan-{plan}")


def test_two_started_plans_each_get_their_own_environment_agent_and_chat(app: App, supervisors: Supervisors):
    user_set(app, SWITCH, True)
    first, second = started_plan(app, "the floors"), started_plan(app, "the roof")
    assert [launch[0] for launch in supervisors.launches] == [f"plan-{first}", f"plan-{second}"], "each started plan launches its own agent in an environment of its own"
    plans, agents = app.container.get(Plans), app.container.get(Agents)
    for plan in (first, second):
        [agent] = agents.global_matching(id=plans.agent_id(plans.find(plan)))
        assert agent.environment_id == plan_environment(app, plan).row_id and agent.state == "leading_plan", "the plan's plan_agent link names the agent of its own environment, on a Plan agent's floor"
    assert [plans.find(plan).state for plan in (first, second)] == [PlanState.STARTED, PlanState.STARTED], "the main agent delegates, so starting the second plan pauses neither"
    with app.container.get(Scope).environment(plan_environment(app, first).row_id):
        assert [plan.id for plan in plans.scoped()] == [first] and len(plans.plan_tasks(plans.find(first))) == 1, "the first plan's environment reads its plan and its tasks, not the other plan"
    status, answer = posted(app, "/journal/messages", {"text": "how are the floors?"}, {"X-Journal-Env": f"plan-{first}"})
    assert status < 400, answer
    chat = lambda environment_id: [message.text for message in app.container.get(Messages).global_matching(environment_id=environment_id)]
    assert "how are the floors?" in chat(plan_environment(app, first).row_id) and "how are the floors?" not in chat(MAIN), "the user's words in the plan's chat are that environment's alone"
    assert app.container.get(PlanOutline).build(plans.find(first))["chat"] == f"plan-{first}", "the plan's outline names the chat its card opens"
    assert f"Plan agent: environment plan-{first}, running" in app.console().run(["plan", "show", str(first)], AGENT).text, "plan show names the plan's environment and that its agent runs"


def test_a_plan_agents_first_session_takes_the_prepared_row_and_follows_its_plan(app: App, supervisors: Supervisors):
    user_set(app, SWITCH, True)
    plan = started_plan(app, "the floors")
    plans, agents = app.container.get(Plans), app.container.get(Agents)
    prepared = plans.agent_id(plans.find(plan))
    status, answer = posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "plan-session"}, {"X-Journal-Env": f"plan-{plan}"})
    assert status < 400, answer
    [agent] = agents.global_matching(id=prepared)
    assert agent.session == "plan-session" and agent.previous_sessions == (), "the first session takes the prepared row, which kept no empty session of its own"
    assert [(layer["state"], layer["data"].get("plan_id")) for layer in agent.stack] == [("leading_plan", plan), ("following_plan", plan)], "it leads its plan and follows it"
    told = [entry.data["line"] for entry in app.container.get(Entries).global_matching(entry_type=NUDGE) if entry.data.get("key") == "plans.you_lead_the_plan"]
    assert told == [f"you lead plan {plan} in this worktree; work its tasks here"], "its session start names the plan it leads"


def test_pausing_resuming_and_finishing_a_plan_stops_and_starts_its_agent(app: App, supervisors: Supervisors):
    user_set(app, SWITCH, True)
    plan = started_plan(app, "the floors")
    environment = plan_environment(app, plan)
    plans = app.container.get(Plans)
    prepared = plans.agent_id(plans.find(plan))
    posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "plan-session"}, {"X-Journal-Env": f"plan-{plan}"})
    assert app.console().run(["plan", "pause", str(plan)], USER).code == 0
    app.runtime().deferred.drain()
    assert supervisors.stops == [environment.row_id], "a paused plan's agent is stopped"
    assert app.console().run(["plan", "start", str(plan)], USER).code == 0
    app.runtime().deferred.drain()
    assert supervisors.launches[-1] == (f"plan-{plan}", "claude", ("--resume", "plan-session")), "a resumed plan starts its agent again, carrying on its last conversation"
    assert plan_environment(app, plan).row_id == environment.row_id and plans.agent_id(plans.find(plan)) == prepared, "in the same environment, on the same agent row"
    plans.save(plans.find(plan).finished(1.0), Actor.user(1))
    app.runtime().deferred.drain()
    assert supervisors.stops == [environment.row_id, environment.row_id], "a finished plan's agent is stopped"


def test_with_plan_agents_off_a_started_plan_starts_no_agent(app: App, supervisors: Supervisors):
    plan = started_plan(app, "the floors")
    plans = app.container.get(Plans)
    assert supervisors.launches == [] and plans.agent_id(plans.find(plan)) == 0, "no agent is launched or linked"
    assert not app.container.get(Environments).matching(name=f"plan-{plan}"), "and no environment is made for the plan"
