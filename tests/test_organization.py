from journal.features.organization.support.approval_action import ApprovalAction
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.edge import Edge
from journal.features.organization.support.edge_kind import EdgeKind
from journal.features.organization.support.role import Role
from journal.features.organization.support.role_models import RoleModels
from journal.features.organization.support.tool_ids import ToolIds
import pytest

from journal.providers.claude import Claude
from journal.providers.codex import Codex
from journal.providers.support.profile_type import ProfileType
from tests.test_features import booted


@pytest.fixture(scope="module")
def boot():
    return booted


def a_role(**changes) -> Role:
    fields = dict(id="builder", title="Builder", domain="alpha", description="Builds what a task asks.", cardinality=Cardinality.MANY, writes=True, responsible=("the change",), not_responsible=("the release",),
                  inputs=("a task",), outputs=("a commit",), edges=(Edge(EdgeKind.DELEGATES_TO, "scout", "what to look up"), Edge(EdgeKind.ESCALATES_TO, "scout", "a blocker")), skills=("governance",),
                  tools=("read_files", "edit_files", "run_tests", "crm"), approval_required=(ApprovalAction.PRODUCTION_DEPLOYMENT,), models=RoleModels("sonnet", "gpt-6-luna", "max"), guidance="Work in small steps.")
    return Role(**{**fields, **changes})


def test_a_role_answers_what_it_may_do_and_is_the_one_value_solo_and_a_seat_both_read():
    builder, scout = a_role(), a_role(id="scout", writes=False, cardinality=Cardinality.JOURNAL, tools=("read_files",), models=RoleModels("opus", "gpt-6.1-sol", "xhigh"))
    assert builder.allows_edits() and builder.has_worktree() and not builder.waits_in_queue(), "a writer on many has a worktree and its own instance"
    assert not scout.allows_edits() and not scout.has_worktree() and scout.waits_in_queue(), "a non-writer has no worktree and a journal Role is queued on"
    assert builder.needs_approval(ApprovalAction.PRODUCTION_DEPLOYMENT) and not builder.needs_approval(ApprovalAction.CONTRACT_CHANGE)
    assert [edge.about for edge in builder.edges_of(EdgeKind.ESCALATES_TO)] == ["a blocker"] and builder.edge_targets() == ("scout",)
    assert builder.models.for_provider("claude") == "sonnet" and builder.models.for_provider("codex") == "gpt-6-luna"
    tools = ToolIds()
    assert tools.words(builder.tools) == "Read, Grep, Glob, Edit, Write, Bash" and tools.is_known("run_tests") and not tools.is_known("crm") and tools.is_well_formed("crm"), "tool ids become the provider's words; an external system brings none"
    profile = builder.profile("Shared guidance.", tools.words(builder.tools))
    assert profile.profile_type == ProfileType.WORKER and scout.profile("", "Read").profile_type == ProfileType.SUBAGENT
    assert profile.body.startswith("Shared guidance.\n\nWork in small steps.") and "- the release" in profile.body, "the body is the domain's guidance, the Role's and its duties"
    for provider in (Claude(), Codex()):
        text = provider.profile_text(profile, builder.models.claude, builder.models.codex)
        assert "builder" in text and "Work in small steps." in text, f"{provider.name} renders the same Role"


def loaded(app, tmp_path, **setup):
    from journal.features.organization.support.organization import Organization
    from tests.organization_fixture import OrganizationFixture
    from tests.user_settings import user_set
    fixture = OrganizationFixture(tmp_path / "organization").write()
    user_set(app, "workers.organization_folder", str(fixture.root))
    return fixture, app.container.get(Organization)


def test_the_loader_reads_the_domains_and_roles_the_folder_holds_and_ignores_what_is_not_one(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    contracts = organization.contracts()
    assert contracts.problems == () and [domain.id for domain in contracts.domains] == ["alpha", "beta"] and sorted(role.id for role in contracts.roles) == ["builder", "keeper", "scout"], "two domains and three Roles, the empty ghost folder ignored"
    builder = contracts.role("builder")
    assert builder.cardinality is Cardinality.MANY and builder.writes and builder.models.codex == "gpt-6-luna" and builder.skills == ("ids",) and builder.guidance == "Guidance of builder.\n" and builder.edges == (Edge(EdgeKind.DELEGATES_TO, "scout", "what to look up"),)
    assert contracts.cardinality_of("scout") is Cardinality.JOURNAL and contracts.role("keeper").needs_approval(ApprovalAction.CONTRACT_CHANGE) and contracts.domain("alpha").guidance == "Guidance of alpha.\n"
    graph = contracts.graph()
    assert [edge.declared for edge in graph].count(True) == 2 and any(edge.source == "plan" and edge.target == "domain:alpha" and not edge.declared for edge in graph), "containment edges and the two declared ones"
    fixture.domain("gamma", roles=["pilot"])
    fixture.role("gamma", "pilot")
    assert organization.contracts().role("pilot") is None and organization.reload().role("pilot").domain == "gamma", "a new domain and Role are seen after a reload with no code change"


@pytest.mark.parametrize("domain, role, changes, rule, path", [
    ("alpha", "builder", {"writes": True, "tools": ["read_files", "edit_files"], "model": {"claude": "sonnet", "codex": {"model": "gpt-6.1-sol", "effort": "xhigh"}}}, "model", "domains/alpha/roles/builder/role.toml"),
    ("alpha", "scout", {"cardinality": "worktree"}, "cardinality", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"skills": ["Task-selected repository SKILL.md knowledge"]}, "skills", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"approval_required": ["fly_to_the_moon"]}, "approval", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"edges": [{"kind": "befriends", "to": "builder", "about": "x"}]}, "edge", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"edges": [{"kind": "delegates_to", "to": "ghostly", "about": "x"}]}, "edge", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"edges": [{"kind": "delegates_to", "to": "keeper", "about": "x"}]}, "edge", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"writes": True}, "tools", "domains/alpha/roles/scout/role.toml"),
])
def test_a_role_that_breaks_the_schema_is_left_out_and_reported_and_its_neighbours_are_kept(app, tmp_path, domain, role, changes, rule, path):
    fixture, organization = loaded(app, tmp_path)
    fixture.role(domain, role, **{"cardinality": "journal", "tools": ["read_files"], **changes})
    contracts = organization.reload()
    assert any(problem.rule == rule and problem.path == path for problem in contracts.problems), [(problem.rule, problem.path) for problem in contracts.problems]
    assert contracts.role(role) is None and contracts.role("keeper") is not None, "the file is left out whole, the others stay"


def test_a_domain_edge_to_an_unknown_domain_a_role_file_that_does_not_parse_and_a_role_folder_without_its_toml_are_reported(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    fixture.domain("beta", roles=["keeper"], edges=[{"kind": "escalates_to", "to": "nowhere", "about": "x"}])
    (fixture.root / "domains" / "alpha" / "roles" / "builder" / "role.toml").write_text("this is = = not toml")
    stray = fixture.root / "domains" / "alpha" / "roles" / "stray"
    stray.mkdir()
    (stray / "AGENTS.md").write_text("no contract\n")
    found = {(problem.rule, problem.path) for problem in organization.reload().problems}
    assert ("edge", "domains/beta/domain.toml") in found and ("parse", "domains/alpha/roles/builder/role.toml") in found and ("role", "domains/alpha/roles/stray") in found


def test_no_folder_set_is_no_organization_and_a_folder_that_is_missing_is_one_problem(app, tmp_path):
    from journal.features.organization.support.organization import Organization
    from tests.user_settings import user_set
    organization = app.container.get(Organization)
    assert organization.reload().is_empty() and organization.contracts().problems == (), "an empty setting is no organization and no problem"
    user_set(app, "workers.organization_folder", str(tmp_path / "missing"))
    assert [problem.rule for problem in organization.reload().problems] == ["folder"]


def test_journal_organization_lists_the_roles_of_each_domain_with_their_cardinality(app, tmp_path):
    from journal.support.caller import Caller
    loaded(app, tmp_path)
    shown = app.console().run(["organization", "list"], Caller.agent("main", "s1", "claude")).text
    assert "domain alpha: Alpha" in shown and "  role builder: many, writes, claude sonnet, codex gpt-6-luna on max" in shown and "  role keeper: plan, does not write" in shown and "version " in shown


def test_a_job_dispatched_to_a_role_starts_with_that_roles_and_its_domains_guidance_and_its_model(app, tmp_path, monkeypatch):
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.repositories.workers import Workers
    from journal.supervisor_link import SupervisorLink
    from journal.support.caller import Caller
    from tests.test_features import hook
    from tests.worker_dispatch import dispatched
    started = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: None)
    monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: started.append(worker))
    fixture, organization = loaded(app, tmp_path)
    fixture.role("beta", "porter", cardinality="plan", writes=True, tools=["read_files", "edit_files"], skills=["ids"], model=fixture.model("sonnet", True))
    fixture.domain("beta", roles=["keeper", "porter"])
    organization.reload()
    agent = Caller.agent("main", "s1", "claude")
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], agent)
    refused = lambda *argv: dispatched(console, ["Ada Lovelace", "the job", "--changes", "the files of its task", *argv], agent)
    assert "one of them" in refused().error and "one of them" in refused("--role", "porter", "--profile", "journal-medior").error, "a job names a profile or a Role, one of them"
    assert "no Role" in refused("--role", "nobody").error and "does not write" in refused("--role", "scout").error, "an unknown Role and a Role that does not write are refused"
    sent = refused("--role", "porter", "--provider", "claude")
    assert sent.code == 0, sent.error
    [worker] = started
    assert worker.model == "sonnet" and worker.profile is None, "the Role's model for the provider, and no profile"
    assert worker.role == "porter" and worker.contract == organization.contracts().version, "the worker records its Role and the version of the contracts it began on"
    instructions = app.container.get(WorkerRunner).instructed(worker)
    assert "Guidance of beta." in instructions and "Guidance of porter." in instructions and "Read these skills before you work: ids." in instructions and "the job" in instructions, "the domain's and the Role's guidance, its skills and the job"


def test_a_worker_dispatched_to_a_role_is_refused_a_write_without_a_write_tool_and_an_approval_required_action_waits_for_the_user(app, tmp_path):
    from pathlib import Path
    from journal.engine.support.settings import Settings
    from journal.events.agent.tool_starting import ToolStarting
    from journal.events.feature_data import FeatureData
    from journal.features.organization.organization_nudges import OrganizationNudges
    from journal.features.organization.role_conduct import RoleConduct
    from journal.features.organization.support.organization_data import OrganizationData
    from journal.features.tasks.states.ready import Ready
    from journal.features.workers.support.workers_data import WorkersData
    from journal.models.worker import Worker
    from tests.test_engine import CLASSIFIER
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "deployer", writes=True, tools=["read_files", "edit_files"], approval_required=["production_deployment"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "deployer"])
    contracts = organization.reload()

    def asked(role: str, tool: str, arguments: dict):
        worker = Worker(environment_id=1, name="Ada Lovelace", brief="b", role=role)
        call = Claude().call(tool, arguments, frozenset(), CLASSIFIER)
        data = FeatureData({"workers": WorkersData((), (), 0, (), Path("/w"), (), session_workers=(worker,) if role else ()), "organization": OrganizationData(contracts)})
        return RoleConduct.on_tool_starting(Ready(), ToolStarting(call=call).with_data(data), Settings({}))

    assert asked("scout", "Write", {"file_path": "a.py", "content": "x"}).refusal == OrganizationNudges.ROLE_WRITES_NOTHING.create(role="scout"), "a Role without a write tool is refused a write"
    assert asked("builder", "Write", {"file_path": "a.py", "content": "x"}).refusal is None and asked("scout", "Read", {"file_path": "a.py"}).refusal is None, "a Role with one writes, and reading is not writing"
    assert asked("deployer", "Bash", {"command": "gh workflow run deploy.yml"}).refusal == OrganizationNudges.ACTION_WAITS_FOR_USER.create(action="production_deployment"), "an approval-required action waits for the user"
    assert asked("builder", "Bash", {"command": "gh workflow run deploy.yml"}).refusal is None, "an action the Role does not list is not held"
    assert asked("", "Write", {"file_path": "a.py", "content": "x"}).refusal is None and asked("ghost", "Write", {"file_path": "a.py", "content": "x"}).refusal is None, "a worker with no Role, or one the folder no longer holds, is let through"


def test_a_domain_carries_its_icon_and_its_boards_phase_names_and_a_board_with_another_key_is_refused(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    assert organization.contracts().domain("alpha").icon == "🧪" and organization.contracts().domain("alpha").board.done == "Done", "a domain with no [board] has the plain phase names"
    fixture.domain("alpha", roles=["scout", "builder"], board={"in_progress": "Active", "done": "Completed"})
    board = organization.reload().domain("alpha").board
    assert (board.planned, board.in_progress, board.in_review, board.done) == ("Planned", "Active", "In review", "Completed"), "the names the domain gives, the plain ones for the rest"
    fixture.domain("alpha", roles=["scout", "builder"], board={"finished": "Closed", "done": ""})
    contracts = organization.reload()
    assert contracts.domain("alpha") is None and len([problem for problem in contracts.problems if problem.path == "domains/alpha/domain.toml"]) == 2, "an unknown phase and an empty name are each a problem and the domain is left out"


REAL_FOLDER = "/Users/redmarbakker/Code/transportklok/transportklok-workspace/agentic-organization"


@pytest.mark.skipif(not __import__("os").path.isdir(REAL_FOLDER), reason="the workspace's organization folder is not on this machine")
def test_the_real_organization_folder_loads_with_no_problems(app):
    from collections import Counter
    from journal.features.organization.support.organization import Organization
    from tests.user_settings import user_set
    user_set(app, "workers.organization_folder", REAL_FOLDER)
    contracts = app.container.get(Organization).reload()
    assert [(problem.path, problem.rule, problem.message) for problem in contracts.problems] == []
    assert len(contracts.domains) == 13 and Counter(role.cardinality for role in contracts.roles) == {Cardinality.JOURNAL: 24, Cardinality.PLAN: 18, Cardinality.MANY: 8}


def test_dispatch_to_a_role_honours_its_cardinality_one_instance_with_a_queue_for_journal_and_plan_and_a_worktree_of_its_own_for_many(app, tmp_path, monkeypatch):
    from journal.features.organization.support.role_instances import RoleInstances
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.models.support.ref import Ref
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.supervisor_link import SupervisorLink
    from journal.support.actor import Actor
    from journal.support.caller import Caller
    from tests.test_features import hook
    from tests.worker_dispatch import dispatched
    started = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: None)
    monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: started.append(worker))
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "steward", cardinality="journal", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.role("beta", "porter", cardinality="plan", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "steward"])
    fixture.domain("beta", roles=["keeper", "porter"])
    contracts = organization.reload()
    agent = Caller.agent("main", "s1", "claude")
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], agent)
    from journal.repositories.scope import Scope
    with app.container.get(Scope).environment(1):
        workers = app.container.get(Workers)
        send = lambda name, *argv: dispatched(console, [name, f"the job of {name}", "--changes", "the files of its task", *argv], agent)

        first = send("Ada Lovelace", "--role", "steward")
        assert first.code == 0 and len(started) == 1, first.error
        second = send("Grace Hopper", "--role", "steward")
        assert second.code == 0 and len(started) == 1 and len(workers.role_instances("steward")) == 1, "a second job for a journal Role starts no second instance"
        assert [task.id for task in app.container.get(Tasks).queue(Ref.build(workers.role_instances("steward")[0]))] == [2], "the second job waits in the one instance's queue"

        assert "worktree of its own" in send("Ida Rhodes", "--role", "builder").error and len(started) == 1, "a many Role asks for a worktree of its own and starts nothing without it"

        instances = app.container.get(RoleInstances)
        porter = contracts.role("porter")
        task = app.container.get(Tasks).find(1)
        workers.save(Worker(environment_id=1, name="Edith Clarke", brief="b", role="porter", plan_id=7, state=WorkerState.REPORTED), Actor.system())
        workers.save(Worker(environment_id=1, name="Mary Kenneth", brief="b", role="porter", plan_id=8, state=WorkerState.DISPATCHED), Actor.system())
        assert instances.existing(contracts.role("builder"), task) is None, "many has no instance to join"
        assert instances.existing(porter, task) is None, "a task in no plan is a plan of its own, so a plan Role starts an instance for it"
        monkeypatch.setattr(RoleInstances, "plan_of", lambda self, task: 8)
        assert instances.existing(porter, task).name == "Mary Kenneth", "a plan Role has one instance for each plan"
        monkeypatch.setattr(RoleInstances, "plan_of", lambda self, task: 9)
        assert instances.existing(porter, task) is None, "and another plan gets its own"


def test_a_send_goes_only_along_the_hubs_and_a_send_from_one_role_to_another_is_refused_with_the_hub_to_use(app, tmp_path):
    from journal.features.organization.support.hub_routes import HubRoutes
    from journal.features.workers.support.worker_actions import WorkerActions
    from journal.models.worker import Worker
    from journal.repositories.scope import Scope
    from journal.repositories.workers import Workers
    from journal.support.actor import Actor
    from journal.support.rejection import Rejection
    loaded(app, tmp_path)
    routes = app.container.get(HubRoutes)
    along = [("role:alpha/builder", "domain:alpha"), ("domain:alpha", "role:alpha/scout"), ("domain:alpha", "plan"), ("plan", "domain:beta"), ("plan", "main"), ("main", "plan")]
    across = [("role:alpha/builder", "role:alpha/scout"), ("role:alpha/builder", "domain:beta"), ("domain:alpha", "role:beta/keeper"), ("domain:alpha", "domain:beta"), ("role:alpha/scout", "plan"), ("main", "domain:alpha")]
    assert all(routes.allowed(*pair) for pair in along), "the hubs: Role and Domain agent, Domain agent and Plan agent, Plan agent and main agent"
    assert not any(routes.allowed(*pair) for pair in across), "anything else is sideways"
    with app.container.get(Scope).environment(1):
        workers = app.container.get(Workers)
        sender = workers.save(Worker(environment_id=1, name="Ada Lovelace", brief="b", role="builder", dispatcher="s1"), Actor.system())
        peer = workers.save(Worker(environment_id=1, name="Grace Hopper", brief="b", role="scout", dispatcher="s1"), Actor.system())
        plain = workers.save(Worker(environment_id=1, name="Ida Rhodes", brief="b", dispatcher="s1"), Actor.system())
        refusal = routes.refusal(sender, peer)
        assert "Roles do not send to each other" in refusal and "domain:alpha" in refusal, refusal
        assert routes.refusal(sender, plain) == "" and routes.refusal(plain, peer) == "", "a worker with no Role is not Role traffic"
        with pytest.raises(Rejection, match="Roles do not send"):
            app.container.get(WorkerActions).peer(peer.id, sender.id)


def test_a_changed_contract_is_reported_and_taken_up_by_new_jobs_only_while_the_version_a_job_began_on_is_kept(app, tmp_path):
    from journal.support.caller import Caller
    fixture, organization = loaded(app, tmp_path)
    began = organization.contracts().version
    assert not organization.is_stale(), "nothing changed since it was read"
    fixture.role("beta", "keeper", cardinality="journal", writes=False, tools=["read_files"], approval_required=["contract_change"], model=fixture.model("opus", False))
    agent = Caller.agent("main", "s1", "claude")
    assert organization.is_stale() and "the folder has changed since it was read" in app.console().run(["organization", "list"], agent).text, "a changed folder is reported where it is listed"
    assert organization.contracts().role("keeper").cardinality is Cardinality.PLAN, "a running journal keeps what it read until it is told to read again"
    changed = organization.reload().version
    assert changed != began and not organization.is_stale()
    assert organization.at(began).role("keeper").cardinality is Cardinality.PLAN and organization.at(changed).role("keeper").cardinality is Cardinality.JOURNAL, "a job that began on the first version still sees it; a new job sees the second"


def test_the_contracts_are_read_at_the_git_version_the_setting_names_and_a_version_that_is_not_there_is_reported(app, tmp_path):
    from journal.features.organization.support.organization import Organization
    from journal.support.inner_repositories import InnerRepositories
    from tests.organization_fixture import OrganizationFixture
    from tests.user_settings import user_set
    repository = tmp_path / "repository"
    fixture = OrganizationFixture(repository / "agentic-organization").write()
    git = lambda *argv: InnerRepositories.git(repository, "-c", "user.name=Test", "-c", "user.email=test@example.com", *argv)
    assert git("init", "-q").returncode == 0
    git("add", "-A")
    assert git("commit", "-q", "-m", "first").returncode == 0
    first = git("rev-parse", "HEAD").stdout.strip()
    fixture.role("beta", "keeper", cardinality="journal", writes=False, tools=["read_files"], approval_required=["contract_change"], model=fixture.model("opus", False))
    git("add", "-A")
    assert git("commit", "-q", "-m", "second").returncode == 0
    user_set(app, "workers.organization_folder", str(fixture.root))
    organization = app.container.get(Organization)
    assert organization.reload().role("keeper").cardinality is Cardinality.JOURNAL, "with no version the files as they are checked out"
    user_set(app, "workers.organization_version", first)
    read = organization.reload()
    assert read.problems == () and read.role("keeper").cardinality is Cardinality.PLAN and read.role("scout") is not None, "at the first version the Role was still a plan Role"
    user_set(app, "workers.organization_version", "no-such-version")
    problems = organization.reload().problems
    assert [problem.rule for problem in problems] == ["version"] and "not a commit" in problems[0].message


def test_a_task_handed_or_queued_to_a_role_is_tied_to_its_domain_and_each_domain_lists_its_plans_with_only_its_tasks(app, tmp_path):
    from datetime import datetime, timezone
    from journal.features.organization.support.domain_plans import DomainPlans
    from journal.models.link import Link
    from journal.models.plan import Plan
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.domain_rows import DomainRows
    from journal.repositories.links import Links
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import PLAN_LINK, Tasks
    from journal.repositories.workers import Workers
    from journal.support.actor import Actor
    from journal.support.caller import Caller
    loaded(app, tmp_path)[1].reload()
    tasks, workers, plans, links, domains, domain_plans = (app.container.get(kind) for kind in (Tasks, Workers, Plans, Links, DomainRows, DomainPlans))
    actor = Actor.system()
    with app.container.get(Scope).environment(1):
        plan = plans.save(Plan(environment_id=1, title="the floors"), actor)
        built, kept, looked, loose = (tasks.save(Task(environment_id=1, title=title, brief=f"{title} reads"), actor) for title in ("the build", "the contract", "the lookup", "the loose end"))
        for task in (built, kept, looked, loose):
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
        builder, keeper, senior = (workers.save(Worker(environment_id=1, name=name, brief="b", profile="journal-senior", role=role), actor) for name, role in (("Mr. Brunel", "builder"), ("Ms. Hopper", "keeper"), ("Mr. Babbage", "")))
        tasks.handover(built, Ref.build(builder), actor)
        tasks.queued(looked, Ref.build(builder), actor)
        tasks.queued(kept, Ref.build(keeper), actor)
        tasks.handover(loose, Ref.build(senior), actor)
        alpha, beta = domain_plans.of("alpha"), domain_plans.of("beta")
        assert [(line.plan.id, [task.id for task in line.tasks]) for line in alpha] == [(plan.id, [built.id, looked.id])], "the plan lists under alpha with alpha's tasks alone, the one handed to no Role left out"
        assert [(line.plan.id, [task.id for task in line.tasks]) for line in beta] == [(plan.id, [kept.id])], "the same plan lists under beta with beta's task alone"
        assert alpha[0].is_active() and beta[0].is_active(), "a Role of each domain holds one of its tasks"
        tasks.save(tasks.find(kept.id).completed(datetime.now(timezone.utc), "kept"), actor)
        assert not domain_plans.of("beta")[0].is_active() and domain_plans.of("alpha")[0].is_active(), "beta's task done, no Role of beta holds the plan; alpha still does"
        domains.task_tied(tasks.find(looked.id), "beta", actor)
        assert [task.id for task in domain_plans.of("alpha")[0].tasks] == [built.id] and [task.id for task in domain_plans.of("beta")[0].tasks] == [kept.id, looked.id], "a task handed on to another domain's Role belongs to that domain alone"
    shown = app.console().run(["organization", "plans"], Caller.agent("main", "s1", "claude")).text
    assert f"domain alpha: Alpha\n  plan {plan.id} the floors, Planned, active: task {built.id} open\ndomain beta: Beta\n  plan {plan.id} the floors, Planned, active: task {kept.id} completed, task {looked.id} open" in shown


def test_a_plan_stands_in_the_phase_each_domains_tasks_reached_on_that_domains_board_by_the_names_the_domain_gives(app, tmp_path):
    from datetime import datetime, timezone
    from journal.events.bus import Bus
    from journal.events.listener import Listener
    from journal.events.rows.plan_entered_board_phase import PlanEnteredBoardPhase
    from journal.features.organization.support.domain_plans import DomainPlans
    from journal.models.board_phase import BoardPhase
    from journal.models.link import Link
    from journal.models.plan import Plan
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.repositories.links import Links
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import PLAN_LINK, Tasks
    from journal.repositories.workers import Workers
    from journal.support.actor import Actor
    from journal.support.caller import Caller
    fixture, organization = loaded(app, tmp_path)
    fixture.domain("alpha", roles=["scout", "builder"], board={"in_progress": "Being built", "done": "Implemented"})
    organization.reload()
    entered = []

    class Entered(Listener[PlanEnteredBoardPhase]):
        def handle(self, event: PlanEnteredBoardPhase) -> None:
            entered.append((event.plan_id, event.domain, event.phase))

    app.container.get(Bus).listen(PlanEnteredBoardPhase, Entered())
    tasks, workers, plans, links, domain_plans = (app.container.get(kind) for kind in (Tasks, Workers, Plans, Links, DomainPlans))
    actor, now = Actor.system(), datetime.now(timezone.utc)
    with app.container.get(Scope).environment(1):
        plan = plans.save(Plan(environment_id=1, title="the floors"), actor)
        built, kept, loose = (tasks.save(Task(environment_id=1, title=title, brief=f"{title} reads"), actor) for title in ("the build", "the contract", "the loose end"))
        for task in (built, kept, loose):
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
        builder, keeper = (workers.save(Worker(environment_id=1, name=name, brief="b", profile="journal-senior", role=role), actor) for name, role in (("Mr. Brunel", "builder"), ("Ms. Hopper", "keeper")))
        tasks.handover(built, Ref.build(builder), actor)
        tasks.handover(kept, Ref.build(keeper), actor)
        assert [line.phase() for line in (*domain_plans.of("alpha"), *domain_plans.of("beta"))] == [BoardPhase.PLANNED, BoardPhase.PLANNED], "a domain task exists in the plan and none is started"
        tasks.save(tasks.find(built.id).worker_started(now), actor)
        tasks.save(tasks.find(kept.id).worker_started(now), actor)
        workers.save(workers.find(keeper.id).with_(state=WorkerState.DELIVERED), actor)
        assert (domain_plans.of("alpha")[0].phase(), domain_plans.of("beta")[0].phase()) == (BoardPhase.IN_PROGRESS, BoardPhase.IN_REVIEW), "alpha's task is worked; beta's worker clocked out and its proofs wait to be checked"
        tasks.save(tasks.find(kept.id).completed(now, "kept"), actor)
        assert (domain_plans.of("alpha")[0].phase(), domain_plans.of("beta")[0].phase()) == (BoardPhase.IN_PROGRESS, BoardPhase.DONE), "beta is done with its task while alpha and a task of no domain are still open"
    assert [(n, domain, phase) for n, domain, phase in entered if n == plan.id] == [(plan.id, "alpha", BoardPhase.PLANNED), (plan.id, "beta", BoardPhase.PLANNED), (plan.id, "alpha", BoardPhase.IN_PROGRESS), (plan.id, "beta", BoardPhase.IN_PROGRESS), (plan.id, "beta", BoardPhase.IN_REVIEW), (plan.id, "beta", BoardPhase.DONE)], "each phase a plan enters on a board fires once, in order"
    shown = app.console().run(["organization", "plans"], Caller.agent("main", "s1", "claude")).text
    assert f"domain alpha: Alpha\n  plan {plan.id} the floors, Being built, active: task {built.id} started\ndomain beta: Beta\n  plan {plan.id} the floors, Done: task {kept.id} completed" in shown, "each board names the phase by its domain's own name"


def test_a_role_that_is_stuck_refused_or_ends_without_clocking_out_is_reported_to_its_domain_agent_then_the_plan_agent_then_the_user(app, tmp_path):
    from journal.events.agent.impasse_report import ImpasseReport
    from journal.events.agent.line_delivered import LineDelivered
    from journal.events.bus import Bus
    from journal.events.listener import Listener
    from journal.events.rows.role_escalated import RoleEscalated
    from journal.features.organization.listeners.role_refusal_report import RoleRefusalReport
    from journal.features.organization.listeners.role_stuck_report import RoleStuckReport
    from journal.features.organization.organization_nudges import OrganizationNudges
    from journal.features.organization.support.role_escalation import ESCALATED_LINK
    from journal.models.agent import Agent
    from journal.models.plan import Plan
    from journal.models.worker import Worker
    from journal.repositories.agents import Agents
    from journal.repositories.domain_rows import DomainRows
    from journal.repositories.links import Links
    from journal.repositories.messages import Messages
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.workers import Workers
    from journal.support.actor import Actor
    loaded(app, tmp_path)[1].reload()
    escalated = []

    class Escalated(Listener[RoleEscalated]):
        def handle(self, event: RoleEscalated) -> None:
            escalated.append((event.recipient, event.report))

    app.container.get(Bus).listen(RoleEscalated, Escalated())
    agents, workers, plans, domains, links, scope = (app.container.get(kind) for kind in (Agents, Workers, Plans, DomainRows, Links, Scope))
    actor = Actor.system()
    with scope.environment(1):
        plan = plans.save(Plan(environment_id=1, title="the floors"), actor)
        domain_agent, plan_agent, gone = (agents.save(Agent(environment_id=1, session=session, provider="claude", state=state), actor) for session, state in (("domain-alpha", "idle"), ("plan-1", "idle"), ("domain-beta", "ended")))
        domains.agent_linked("alpha", domain_agent, actor)
        domains.agent_linked("beta", gone, actor)
        plans.agent_linked(plan, plan_agent, actor)
        builder, keeper, franklin = (workers.save(Worker(environment_id=1, name=name, brief="b", profile="journal-senior", role=role, plan_id=plan_id, session=session, dispatcher="s1"), actor)
                                     for name, role, plan_id, session in (("Mr. Brunel", "builder", plan.id, "w-brunel"), ("Ms. Hopper", "keeper", plan.id, "w-hopper"), ("Ms. Franklin", "keeper", 0, "w-franklin")))
        app.container.get(RoleStuckReport).handle(ImpasseReport(reason="the schema is missing").placed("w-brunel", 1, "claude", None, 1.0))
        assert escalated == [("domain-alpha", f"the Role builder of alpha is stuck: the schema is missing (worker {builder.id}, Mr. Brunel)")], "step one: a stuck Role is reported to its Domain agent"
        app.container.get(RoleRefusalReport).handle(LineDelivered(nudge=OrganizationNudges.ROLE_WRITES_NOTHING.key, values={"role": "keeper"}).placed("w-hopper", 1, "claude", None, 2.0))
        assert escalated[-1] == ("plan-1", f"the Role keeper of beta was refused: your Role keeper has no write tool: change no file (worker {keeper.id}, Ms. Hopper)"), "step two: its Domain agent ended, a refused Role is reported to the Plan agent"
        workers.save(workers.find(franklin.id).unfinished(3.0, "stopped after 30 minutes without ending: (nothing printed)"), actor)
        cards = [message for message in app.container.get(Messages).all() if message.text == "Role reported to you"]
    assert len(escalated) == 2 and len(cards) == 1 and cards[0].data["lines"] == ["the Role keeper of beta ended without clocking out", "stopped after 30 minutes without ending: (nothing printed)", f"worker {franklin.id}, Ms. Franklin"] and cards[0].session == "s1", "step three: with no Domain agent running and no plan, a Role that timed out is reported to the user in its dispatcher's chat"
    assert ([ref.id for ref in links.targets(builder, ESCALATED_LINK)], [ref.id for ref in links.targets(keeper, ESCALATED_LINK)]) == ([domain_agent.id], [plan_agent.id]), "each report to an agent is a link from the worker to it"
