"""Plan agents: with the switch on, a started plan runs in its own environment plan-<n> with its own agent and chat, started at the plan's start and stopped at its pause or end; a plan is its owner's to approve, and its agent's chat is seen as the plan's own environment is."""

from dataclasses import replace

import pytest

from journal.app import App
from journal.engine.agent_launcher import AgentLauncher
from journal.http.agents.agent_activity import AgentActivity
from journal.http.plans.plan_outline import PlanOutline
from journal.models.plan_state import PlanState
from journal.repositories.agents import Agents
from journal.repositories.entries import NUDGE, Entries
from journal.repositories.environment_owners import EnvironmentOwners
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
    with app.container.get(Scope).environment(plan_environment(app, plan).row_id):
        [row] = [item for item in app.container.get(AgentActivity).page(agents.scoped()) if item["session"] == "plan-session"]
    [pushed] = [entry["after"] for entry in row["trail"] if len(entry["after"]) == 2]
    assert pushed[0] == f"leading_plan (plan {plan})" and pushed[1].startswith(f"following_plan (plan {plan}"), "the trail names each state pushed with the plan it is about"


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


def test_a_plan_is_its_owners_to_approve_and_its_agents_chat_is_seen_as_the_plans_environment_is(app: App, supervisors: Supervisors):
    user_set(app, SWITCH, True)
    owners, plans, environments, console = app.container.get(EnvironmentOwners), app.container.get(Plans), app.container.get(Environments), app.console()
    owner = owners.owner_number(MAIN)
    assert owner, "the main environment is its person's"
    colleague = replace(USER, person=owner + 1)
    plan = int(console.run(["plan", "create", "the floors", "--brief", "the floors are laid"], USER).text.split()[1].rstrip(":"))
    console.run(["plan", "add", str(plan), "the first board"], USER)
    assert f"owner: {owners.person_name(owner)}" in console.run(["plan", "show", str(plan)], AGENT).text, "plan show names the person the plan is of"
    assert app.container.get(PlanOutline).build(plans.find(plan))["owner"] == owners.person_name(owner), "and so does its page"
    refused = console.run(["plan", "approve", str(plan)], colleague)
    assert refused.code != 0 and owners.person_name(owner) in refused.error and plans.find(plan).state == PlanState.DRAFT, "a colleague's approval is refused, naming the plan's owner"
    assert console.run(["plan", "approve", str(plan)], USER).code == 0, "its owner approves it"
    assert console.run(["plan", "start", str(plan)], USER).code == 0
    app.runtime().deferred.drain()
    private = plan_environment(app, plan)
    assert owners.owner_number(private.row_id) == owner and private.creator == Actor.user(owner) and private.is_private(), "its agent's environment is made by the person who started it, is theirs, and is as private as the plan's own environment"
    posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "plan-session"}, {"X-Journal-Env": f"plan-{plan}"})
    other = int(console.run(["plan", "create", "the roof", "--brief", "the roof is on"], USER).text.split()[1].rstrip(":"))
    console.run(["plan", "add", str(other), "the first tile"], USER)
    assert console.run(["plan", "approve", str(other)], Caller.agent(f"plan-{plan}", "plan-session", "claude")).code != 0 and plans.find(other).state == PlanState.DRAFT, "a Plan agent approves no plan"
    environments.save(environments.find(MAIN).shared_with_team("team-key"), Actor.user(owner))
    assert console.run(["plan", "approve", str(other)], USER).code == 0 and console.run(["plan", "start", str(other)], USER).code == 0
    app.runtime().deferred.drain()
    assert plan_environment(app, other).team_key == "team-key", "the agent of a plan in a shared environment has a chat the team sees"


def test_a_solo_plan_agent_acting_as_a_review_role_is_refused_a_write(app: App, supervisors: Supervisors, tmp_path):
    from journal.features.organization.support.organization import Organization
    from tests.organization_fixture import OrganizationFixture
    fixture = OrganizationFixture(tmp_path / "organization").write()
    user_set(app, "workers.organization_folder", str(fixture.root))
    keeper = app.container.get(Organization).reload().role("keeper")
    user_set(app, SWITCH, True)
    plan = started_plan(app, "the review")
    plans, agents, console = app.container.get(Plans), app.container.get(Agents), app.console()
    agent_id = plans.agent_id(plans.find(plan))
    lead = Caller.agent(f"plan-{plan}", "plan-session", "claude")
    planned = lambda name, **body: posted(app, "/hooks/claude", {"hook_event_name": name, "session_id": "plan-session", **body}, {"X-Journal-Env": f"plan-{plan}"})
    planned("SessionStart")
    console.run(["environment", "overview"], lead)
    assert console.run(["role", "take", "keeper"], AGENT).code != 0, "only the Plan agent of a solo plan takes on a Role"
    taken = console.run(["role", "take", "keeper"], lead)
    assert taken.code == 0, taken.error
    top = lambda: agents.find(agent_id).stack[-1]
    assert (top()["state"], top()["data"]["role"]) == ("role_work", "keeper"), "the Role is pushed as the state of working as it"
    status, body = planned("PreToolUse", tool_name="Write", tool_input={"file_path": "findings.txt", "content": "a finding"})
    assert status == 409 and "has no write tool" in body["error"], "acting as a Role that writes nothing, a write is refused"
    status, body = planned("PreToolUse", tool_name="Read", tool_input={"file_path": "findings.txt"})
    assert status == 200, f"a tool the Role names goes through: {body}"
    assert planned("PreToolUse", tool_name="Bash", tool_input={"command": "journal task list"})[0] == 200, "and a journal command always does"
    guided = lambda: [entry.data["line"] for entry in app.container.get(Entries).global_matching(entry_type=NUDGE) if entry.data.get("key") == "organization.you_act_as_the_role"]
    assert len(guided()) == 1 and keeper.guidance in guided()[0], "its push brings the Role's guidance"
    with app.container.get(Scope).environment(plan_environment(app, plan).row_id):
        [row] = [item for item in app.container.get(AgentActivity).page(agents.scoped()) if item["session"] == "plan-session"]
    assert row["trail"][-1]["after"][-1] == "role_work (Role keeper)", "the trail names the Role it acts as"
    assert console.run(["role", "take", "scout"], lead).code != 0, "a Role every plan shares is never taken on"
    planned("PreCompact")
    planned("SessionStart", source="compact")
    console.run(["environment", "overview"], lead)
    assert top()["state"] == "role_work" and len(guided()) > 1, "after a compaction it is the Role it was, told its guidance again"
    assert console.run(["role", "done"], lead).code == 0 and top()["state"] != "role_work", "the step's end pops it"


def test_a_solo_plans_release_step_waits_in_the_shared_roles_queue(app: App, supervisors: Supervisors, tmp_path):
    from journal.features.organization.support.organization import Organization
    from journal.models.support.ref import Ref
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from tests.organization_fixture import OrganizationFixture
    fixture = OrganizationFixture(tmp_path / "organization").write()
    fixture.role("alpha", "releaser", cardinality="journal", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "releaser"])
    user_set(app, "workers.organization_folder", str(fixture.root))
    app.container.get(Organization).reload()
    with app.container.get(Scope).environment(MAIN):
        instance = app.container.get(Workers).save(Worker(environment_id=MAIN, name="Ada Lovelace", brief="releases", role="releaser", state=WorkerState.DISPATCHED), Actor.system())
    user_set(app, SWITCH, True)
    plan = started_plan(app, "the release")
    console, tasks, plans = app.console(), app.container.get(Tasks), app.container.get(Plans)
    console.run(["plan", "add", str(plan), "the release step"], USER)
    step = max(plans.plan_task_ids(plans.find(plan)))
    lead = Caller.agent(f"plan-{plan}", "plan-session", "claude")
    posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "plan-session"}, {"X-Journal-Env": f"plan-{plan}"})
    console.run(["environment", "overview"], lead)
    queued = console.run(["role", "take", "releaser", "--task", str(step)], lead)
    assert queued.code == 0 and f"task {step} waits in the queue" in queued.text, queued.error
    assert [task.id for task in tasks.queue(Ref.build(instance))] == [step], "the step waits in the queue of the shared Role's one instance, made in the main environment"
    assert app.container.get(Agents).find(plans.agent_id(plans.find(plan))).stack[-1]["state"] != "role_work", "a shared Role is never taken on as a state"
