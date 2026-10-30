"""Plan agents: with the switch on, a started plan runs in its own environment plan-<n> with its own agent and chat, started at the plan's start and stopped at its pause or end; a plan is its owner's to approve, and its agent's chat is seen as the plan's own environment is."""

from dataclasses import replace

import pytest

from journal.app import App
from journal.engine.agent_launcher import AgentLauncher
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.workers.workers_nudges import WorkersNudges
from journal.http.agents.agent_activity import AgentActivity
from journal.http.plans.plan_outline import PlanOutline
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.models.plan_state import PlanState
from journal.repositories.agents import Agents
from journal.repositories.entries import NUDGE, Entries
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.environments import Environments
from journal.repositories.messages import Messages
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.caller import Caller
from journal.support.supervisor_reply import SupervisorReply
from journal.supervisor_link import SupervisorLink
from tests.in_process import get_answer, posted
from tests.nudge_lines import nudge_reached
from tests.organization_fixture import OrganizationFixture
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
    main_key = app.container.get(Environments).find(MAIN).key
    for plan in (first, second):
        [agent] = agents.global_matching(id=plans.agent_id(plans.find(plan)))
        environment = plan_environment(app, plan)
        assert agent.environment_id == environment.row_id and agent.state == "leading_plan", "the plan's plan_agent link names the agent of its own environment, on a Plan agent's floor"
        assert environment.generated_for == "plan" and environment.parent_key == main_key, "the generated Plan environment records its kind and source environment"
    assert [plans.find(plan).state for plan in (first, second)] == [PlanState.STARTED, PlanState.STARTED], "the main agent delegates, so starting the second plan pauses neither"
    with app.container.get(Scope).environment(plan_environment(app, first).row_id):
        assert [plan.id for plan in plans.scoped()] == [first] and len(plans.plan_tasks(plans.find(first))) == 1, "the first plan's environment reads its plan and its tasks, not the other plan"
    status, answer = posted(app, "/journal/messages", {"text": "how are the floors?"}, {"X-Journal-Env": f"plan-{first}"})
    assert status < 400, answer
    chat = lambda environment_id: [message.text for message in app.container.get(Messages).global_matching(environment_id=environment_id)]
    assert "how are the floors?" in chat(plan_environment(app, first).row_id) and "how are the floors?" not in chat(MAIN), "the user's words in the plan's chat are that environment's alone"
    outline = app.container.get(PlanOutline).build(plans.find(first))
    [first_agent] = agents.global_matching(id=plans.agent_id(plans.find(first)))
    assert outline["chat"] == f"plan-{first}" and outline["plan_agent_last_action_at"] == first_agent.updated_at, "the plan's outline names its chat and when its agent last acted"
    assert f"Plan agent: environment plan-{first}, running" in app.console().run(["plan", "show", str(first)], AGENT).text, "plan show names the plan's environment and that its agent runs"
    status, answer = get_answer(app, "/journal/environments", {"X-Journal-Env": "main"})
    rows = {row["name"]: row for row in answer["rows"]}
    assert status == 200 and rows[f"plan-{first}"]["generated_for"] == "plan" and rows[f"plan-{first}"]["parent_key"] == main_key, "the environment list exposes authoritative generated and parent metadata"


def test_a_plan_agent_stop_shows_the_supervisors_plain_refusal(app: App, supervisors: Supervisors, monkeypatch):
    user_set(app, SWITCH, True)
    plan = started_plan(app, "the floors")
    environment = plan_environment(app, plan)
    refusal = "Cannot stop while a merge is in progress; finish the merge first."
    monkeypatch.setattr(SupervisorLink, "stop", lambda self, environment_id: SupervisorReply(False, refusal))

    status, answer = posted(app, f"/journal/environments/{environment.row_id}/stop", {}, {"X-Journal-Env": "main"})

    assert status == 409 and refusal in str(answer), "a refusal from the supervisor reaches the Plan agent's confirmation as plain text"


def test_a_plans_timeline_includes_handoffs_and_refusals_from_its_plan_agents_chat(app: App, supervisors: Supervisors):
    from journal.models.message import Message

    user_set(app, SWITCH, True)
    plan = started_plan(app, "the floors")
    environment = plan_environment(app, plan)
    agents = app.container.get(Agents)
    route = "worker 12 works as the Role builder and worker 13 as scout: Roles do not send to each other. Send it to your Domain agent, domain:alpha, which passes it on"
    with app.container.get(Scope).environment(environment.row_id):
        agent = agents.find(app.container.get(Plans).agent_id(app.container.get(Plans).find(plan)))
        agents.save(agent.with_session("plan-session", "claude"), Actor.system())
        messages = app.container.get(Messages)
        messages.recorded(Message.outgoing("domain:alpha", "please check the file", "plan-session", "domain:alpha"), Actor.agent("plan-session"))
        messages.recorded(Message.send_failed("worker 13, Scout", "send this directly", "plan-session", "workers:13", route), Actor.agent("plan-session"))
    with app.container.get(Scope).environment(MAIN):
        app.container.get(Messages).recorded(Message.outgoing("unrelated", "not this plan", "main-session", "main"), Actor.agent("main-session"))

    status, moments = get_answer(app, f"/journal/plans/{plan}/timeline", {"X-Journal-Env": "main"})
    communication = [moment for moment in moments if moment["moment_type"] in ("handoff", "refused_send")]
    assert status == 200 and [(moment["moment_type"], moment["title"], moment["address"]) for moment in communication] == [
        ("handoff", "domain:alpha", "domain:alpha"), ("refused_send", "worker 13, Scout", "workers:13")
    ], "the timeline reads this plan's outgoing messages across its dedicated environment, not the main chat"
    assert communication[1]["failure"] == route, "a refused send carries the reason and the domain hub to use"


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
    status, ordinary = posted(app, "/journal/environments", {"name": "plan-7"}, {"X-Journal-Env": "main"})
    assert status == 201 and ordinary["generated_for"] == "" and ordinary["parent_key"] == "", "a generic environment named like a generated one stays top-level"


def test_a_nested_plan_agent_environment_records_its_source(app: App, supervisors: Supervisors):
    user_set(app, SWITCH, True)
    parent = started_plan(app, "the outer plan")
    parent_environment = plan_environment(app, parent)
    caller = Caller.user(parent_environment.name)
    console = app.console()
    with app.container.get(Scope).environment(parent_environment.row_id):
        child = int(console.run(["plan", "create", "the inner plan", "--brief", "the inner plan is done"], caller).text.split()[1].rstrip(":"))
        console.run(["plan", "add", str(child), "the inner step"], caller)
        assert console.run(["plan", "approve", str(child)], caller).code == 0
        assert console.run(["plan", "start", str(child)], caller).code == 0
    app.runtime().deferred.drain()
    child_environment = plan_environment(app, child)
    assert child_environment.generated_for == "plan" and child_environment.parent_key == parent_environment.key, "a real nested Plan agent keeps its source relationship"


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
    [step_task] = plans.plan_tasks(plans.find(plan))
    assert (top()["state"], top()["data"]["role"], top()["data"]["task_id"]) == (
        "role_work", "keeper", step_task.row_id
    ), "the Role is pushed with the plan task it took on"
    status, history = got(app, f"/journal/plans/{plan}/roles", {"X-Journal-Env": "main"})
    assert status == 200 and history["current_role"] == "keeper", "the solo plan reports the Role its Plan agent acts as now"
    assert [(step["role"], step["task"], step["title"]) for step in history["steps"]] == [("keeper", step_task.row_id, step_task.title)], "each Role step is linked to its plan task"
    from journal.http.sharing.shared_data import SharedData
    from journal.models.support.ref import Ref
    shared = app.container.get(SharedData).opened(Ref.build(plans.find(plan)))
    assert shared["plans"][0]["plan_agent_roles"] == history, "a shared plan preloads the same Role history without an authenticated journal request"
    status, body = planned("PreToolUse", tool_name="Write", tool_input={"file_path": "findings.txt", "content": "a finding"})
    assert status == 409 and nudge_reached(app, body["error"], OrganizationNudges.ROLE_WRITES_NOTHING, role="keeper"), "acting as a Role that writes nothing, a write is refused"
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
    status, history = got(app, f"/journal/plans/{plan}/roles", {"X-Journal-Env": "main"})
    assert status == 200 and history["current_role"] == "" and len(history["steps"]) == 1, "a finished Role leaves the timeline and no longer appears as current"


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


def test_the_main_agent_runs_two_plans_through_their_plan_agents_without_writing_code(app: App, supervisors: Supervisors, monkeypatch):
    user_set(app, SWITCH, True)
    typed = []
    monkeypatch.setattr(SupervisorLink, "type", lambda self, environment_id, line, following=0.0: typed.append((environment_id, line)))
    first, second = started_plan(app, "the floors"), started_plan(app, "the roof")
    console, messages, plans = app.console(), app.container.get(Messages), app.container.get(Plans)
    for plan in (first, second):
        posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": f"lead-{plan}"}, {"X-Journal-Env": f"plan-{plan}"})
    for plan, job in ((first, "lay the floors"), (second, "put the roof on")):
        told = console.run(["plan", "tell", str(plan), job], AGENT)
        assert told.code == 0, told.error
        app.runtime().deferred.drain()
        [word] = [message for message in messages.global_matching(environment_id=plan_environment(app, plan).row_id) if message.text == job]
        assert word.is_main_unread and word.sender == "the main agent", "the main agent's word is in the plan's chat, unread, from the main agent"
        line = f"new message {word.id} from the main agent"
        assert [environment_id for environment_id, delivered in typed if delivered == line] == [plan_environment(app, plan).row_id], "and is delivered to that plan's agent alone"

    reported = console.run(["plan", "report", "the floors are laid"], Caller.agent(f"plan-{first}", f"lead-{first}", "claude"))
    assert reported.code == 0, reported.error
    app.runtime().deferred.drain()
    [answer] = [message for message in messages.global_matching(environment_id=MAIN) if message.text == "the floors are laid"]
    line = f"new message {answer.id} from the Plan agent of plan {first}"
    assert [environment_id for environment_id, delivered in typed if delivered == line] == [MAIN], "a Plan agent's report reaches the main agent in its chat"
    with app.container.get(Scope).environment(MAIN):
        assert answer.id in [message.id for message in messages.unread()], "the Plan agent's report is a message for the main agent to read"
    assert console.run(["plan", "report", "all is well"], AGENT).code != 0, "only a Plan agent reports"
    draft = int(console.run(["plan", "create", "the garden", "--brief", "a garden"], USER).text.split()[1].rstrip(":"))
    assert console.run(["plan", "tell", str(draft), "dig"], AGENT).code != 0, "a plan with no Plan agent is told nothing"

    for command in (
        "journal worker dispatch 'Ada Lovelace' 'the floors' --changes src",
        "journal worker send 1 'finish the floor'",
    ):
        status, body = hook(app, "PreToolUse", tool_name="Bash", tool_input={"command": command})
        assert status == 409 and nudge_reached(app, body["error"], PlansNudges.COORDINATOR_SENDS_NO_WORKER), f"the main agent refuses {command.split()[2]}"
    status, body = hook(app, "PreToolUse", tool_name="Write", tool_input={"file_path": "src/floors.py", "content": "x"})
    assert status == 409 and nudge_reached(app, body["error"], PlansNudges.COORDINATOR_WRITES_NO_CODE), "the main agent writes no code"
    assert [plans.find(plan).state for plan in (first, second)] == [PlanState.STARTED, PlanState.STARTED], "both plans run side by side"


def test_a_task_outside_every_plan_is_worked_by_an_agent_of_its_own_and_the_main_agent_writes_no_code(app: App, supervisors: Supervisors):
    from journal.features.plans.plans_nudges import PlansNudges
    from journal.features.plans.support.task_agents import TASK_AGENT_LINK
    from journal.features.workers.workers_nudges import WorkersNudges
    from journal.models.support.ref import Ref
    from journal.repositories.links import Links
    from journal.repositories.tasks import Tasks
    from tests.nudge_lines import nudge_reached

    user_set(app, SWITCH, True)
    console, tasks, plans, agents = app.console(), app.container.get(Tasks), app.container.get(Plans), app.container.get(Agents)
    planned = len(plans.global_matching())
    console.run(["task", "create", "fix the footer", "--brief", "the footer names the shop"], AGENT)
    with app.container.get(Scope).environment(MAIN):
        task = tasks.scoped()[-1]
    started = console.run(["task", "start", str(task.id)], AGENT)
    assert started.code == 0, started.error
    app.runtime().deferred.drain()
    assert supervisors.launches[-1][0] == f"task-{task.id}", "the task gets an agent of its own in an environment of its own"
    environment = app.container.get(Environments).existing(f"task-{task.id}")
    agent_id = next(target.id for target in app.container.get(Links).targets(task, TASK_AGENT_LINK))
    agent = agents.find(agent_id)
    assert agent.environment_id == environment.row_id and agent.state == "leading_task" and tasks.holder(tasks.find(task.id)) == Ref.build(agent), "its agent holds it there"
    assert environment.generated_for == "task" and environment.parent_key == app.container.get(Environments).find(MAIN).key, "the generated task environment records its kind and source environment"
    assert len(plans.global_matching()) == planned, "no plan row is made for it"
    assert agents.session_agent("s1").stack[-1]["state"] == "coordinating_plans", "the main agent takes nothing in hand"

    status, session = posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "task-session"}, {"X-Journal-Env": f"task-{task.id}"})
    assert status == 200 and nudge_reached(app, session["hookSpecificOutput"]["additionalContext"], PlansNudges.WORKING_TASK_ALONE, task=task.id), "its first session works the task alone"
    stack = agents.find(agent.id).stack
    assert (stack[0]["state"], stack[-1]["data"].get("task_id")) == ("leading_task", task.id) and len(stack) == 2, "the task agent keeps its standalone floor and works the task"

    def task_hook(tool_name: str, tool_input: dict):
        return posted(app, "/hooks/claude", {"hook_event_name": "PreToolUse", "session_id": "task-session", "tool_name": tool_name, "tool_input": tool_input}, {"X-Journal-Env": f"task-{task.id}"})

    for command in (
        "journal worker dispatch 'Ada Lovelace' 'the floors' --changes src",
        "journal worker send 1 'finish the floor'",
    ):
        status, body = task_hook("Bash", {"command": command})
        assert status == 409 and nudge_reached(app, body["error"], WorkersNudges.SOLO_DISPATCH), f"the task agent refuses {command.split()[2]}"
    task_caller = Caller.agent(f"task-{task.id}", "task-session", "claude")
    assert console.run(["environment", "overview"], task_caller).code == 0, "the task agent reads its environment before working"
    status, body = task_hook("Write", {"file_path": "src/footer.py", "content": "x"})
    assert status == 200, body.get("error", "the task agent may write its own task")

    status, body = hook(app, "PreToolUse", tool_name="Write", tool_input={"file_path": "src/footer.py", "content": "x"})
    assert status == 409, "the main agent writes no code"
    completed = console.run(["task", "complete", str(task.id), "--how", "the footer names the shop"], task_caller)
    assert completed.code == 0, completed.error
    app.runtime().deferred.drain()
    assert environment.row_id in supervisors.stops, "its close stops its agent"


def test_a_plan_agent_can_dispatch_each_read_only_helper_profile(app: App, supervisors: Supervisors):
    user_set(app, SWITCH, True)
    plan = started_plan(app, "the floors")
    environment = plan_environment(app, plan)
    environment_header = {"X-Journal-Env": environment.name}
    status, answer = posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "plan-session"}, environment_header)
    assert status == 200, answer
    for profile in ("journal-researcher", "journal-planner", "journal-debugger", "journal-plan-reviewer"):
        tool_input = {"subagent_type": profile, "model": "sonnet", "description": f"read with {profile}", "prompt": "read the requested files"}
        status, answer = posted(app, "/hooks/claude", {"hook_event_name": "PreToolUse", "session_id": "plan-session", "tool_name": "Agent", "tool_input": tool_input}, environment_header)
        assert status == 200, f"the Plan agent may dispatch {profile}: {answer}"


def test_a_plan_agent_matches_idle_role_workers_by_the_role_contract_name(app: App, supervisors: Supervisors, tmp_path):
    user_set(app, SWITCH, True)
    fixture = OrganizationFixture(tmp_path / "organization").write()
    fixture.role("alpha", "porter", cardinality="many", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "porter"])
    user_set(app, "workers.organization_folder", str(fixture.root))
    user_set(app, "workers.idle_kept", 2)
    plan = started_plan(app, "the floors")
    environment = plan_environment(app, plan)
    environment_header = {"X-Journal-Env": environment.name}
    status, answer = posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "plan-session"}, environment_header)
    assert status == 200, answer
    with app.container.get(Scope).environment(environment.row_id):
        workers = app.container.get(Workers)
        workers.save(Worker(environment_id=environment.row_id, name="Mr. Brunel", role="porter", state=WorkerState.REPORTED), Actor.system())
        workers.save(Worker(environment_id=environment.row_id, name="Ms. Hopper", role="porter", state=WorkerState.REPORTED), Actor.system())
    command = "journal worker dispatch 'Ada Lovelace' 'the job' --changes 'the files of its task' --tests 'Scoped tests' --role porter"
    status, body = posted(app, "/hooks/claude", {"hook_event_name": "PreToolUse", "session_id": "plan-session", "tool_name": "Bash", "tool_input": {"command": command}}, environment_header)
    assert status == 409 and nudge_reached(app, body["error"], WorkersNudges.IDLE_CAP, total=2, profile="porter", count=2), "the Plan agent's idle Role rows match by the Role name through the dispatch check"
