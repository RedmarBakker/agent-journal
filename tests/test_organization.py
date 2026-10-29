from pathlib import Path
from datetime import timedelta

from journal.engine.support.settings import Settings
from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent.tool_starting import ToolStarting
from journal.events.feature_data import FeatureData
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.role_conduct import RoleConduct
from journal.features.organization.listeners.role_refusal_report import RoleRefusalReport
from journal.features.organization.support.approval_action import ApprovalAction
from journal.features.organization.support.approval_actions import ApprovalActions
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.edge import Edge
from journal.features.organization.support.edge_kind import EdgeKind
from journal.features.organization.support.organization_data_reader import OrganizationDataReader
from journal.features.organization.support.role_approvals import RoleApprovals
from journal.features.organization.support.role import Role
from journal.features.organization.support.role_models import RoleModels
from journal.features.organization.support.tool_ids import ToolIds
from journal.support.inner_repositories import InnerRepositories
from journal.features.tasks.states.ready import Ready
from journal.features.workers.support.workers_data import WorkersData
from journal.models.support.ref import Ref
from journal.models.agent import Agent
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.repositories.scope import Scope
from journal.repositories.approvals import Approvals
from journal.repositories.questions import Questions
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
import pytest

from journal.providers.claude import Claude
from journal.providers.codex import Codex
from journal.providers.support.profile_type import ProfileType
from tests.test_features import booted
from tests.test_engine import CLASSIFIER


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
    user_set(app, "workers.organization_folder", "")
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
    assert "--role" in refused().error, "a job names the Role it works as"
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


def test_each_contract_approval_id_is_recognized_from_a_command_and_a_tool():
    for action in ApprovalAction:
        tool = Claude().call(f"mcp__organization__{action.value}", {"action_id": action.value}, frozenset(), CLASSIFIER)
        assert ApprovalActions.of(f"journal role action --approval {action.value}") == (action,)
        assert ApprovalActions.of(tool) == (action,), action.value


def test_an_approved_role_deployment_runs_once_and_a_refusal_stays_refused(app, tmp_path, monkeypatch):
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "deployer", writes=True, tools=["read_files", "edit_files"], approval_required=["production_deployment", "financial_transaction", "contract_change", "security_decision"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "deployer"])
    contracts = organization.reload()
    actor = Actor.user(1)
    scope = app.container.get(Scope)
    with scope.environment(1):
        worker = app.container.get(Workers).save(Worker(name="Ada Lovelace", brief="deploy", session="worker-session", role="deployer", contract=contracts.version), actor)
        tasks = app.container.get(Tasks)
        task = tasks.save(Task(title="release", state=TaskState.STARTED), actor)
        tasks.handover(task, Ref.build(worker), actor)
    approvals = app.container.get(RoleApprovals)
    organization_data = app.container.get(OrganizationDataReader).read(Agent(environment_id=worker.environment_id, session=worker.session))

    def call_for(command: str):
        return Claude().call("Bash", {"command": command}, frozenset(), CLASSIFIER)

    def attempt(command: str):
        data = FeatureData({
            "workers": WorkersData((), (), 0, (), Path("/w"), (), session_workers=(worker,)),
            "organization": organization_data,
        })
        event = ToolStarting(session=worker.session, environment_id=worker.environment_id, call=call_for(command)).with_data(data)
        return RoleConduct.on_tool_starting(Ready(), event, Settings({}))

    def approval_for(command: str, action: ApprovalAction):
        request_hash, _ = ApprovalActions.identity(call_for(command))
        return app.container.get(Approvals).for_action(Actor.agent(worker.session).stamp, worker.role, worker.plan_id, task.row_id, action.value, request_hash)

    deployment = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.PRODUCTION_DEPLOYMENT.value)
    assert attempt("make deploy").refusal == deployment, "the deployment waits before any approval"
    listener = app.container.get(RoleRefusalReport)
    monkeypatch.setattr(listener.escalation, "report", lambda *args: None)
    refusal = LineDelivered(session=worker.session, nudge=OrganizationNudges.ACTION_WAITS_FOR_USER.key, values={"action": ApprovalAction.PRODUCTION_DEPLOYMENT.value})
    with scope.environment(1):
        listener.handle(refusal)
    approved = approval_for("make deploy", ApprovalAction.PRODUCTION_DEPLOYMENT)
    assert approved and (approved.actor, approved.role, approved.task_id, approved.action) == (Actor.agent(worker.session).stamp, "deployer", task.row_id, ApprovalAction.PRODUCTION_DEPLOYMENT)
    assert approved.expires_at is not None and approved.question_id > 0, "the saved request names its answer question and expiry"
    approved = approvals.approve(approved, actor)
    assert approved.updater == actor and approved.decision == approved.APPROVED, "the user's decision is durable"
    assert attempt("make deploy && wire transfer").refusal == deployment, "one approval cannot release a call that carries a second required action"
    assert attempt("make deploy").refusal is None, "the approved deployment passes once"
    assert attempt("make deploy").refusal == deployment, "the same approval is spent after one pass"

    transfer = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.FINANCIAL_TRANSACTION.value)
    assert attempt("wire transfer").refusal == transfer, "a separate approval action waits"
    refused = approval_for("wire transfer", ApprovalAction.FINANCIAL_TRANSACTION)
    refused = approvals.refuse(refused, actor)
    assert attempt("wire transfer").refusal == transfer, "a refusal never lets the action through"
    assert approval_for("wire transfer", ApprovalAction.FINANCIAL_TRANSACTION).row_id == refused.row_id, "a refused exact request stays current instead of opening another question"

    contract_change = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.CONTRACT_CHANGE.value)
    assert attempt("amend contract").refusal == contract_change, "a contract change creates its first request"
    expired = approval_for("amend contract", ApprovalAction.CONTRACT_CHANGE)
    expired = app.container.get(Approvals).save(expired.with_(expires_at=expired.expires_at - timedelta(hours=2)), actor)
    assert attempt("amend contract").refusal == contract_change, "an expired approval cannot authorize a call"
    replacement = approval_for("amend contract", ApprovalAction.CONTRACT_CHANGE)
    with scope.environment(expired.question_environment_id):
        question = app.container.get(Questions).find(expired.question_id)
    assert app.container.get(Approvals).find(expired.row_id).decision == expired.EXPIRED and question.is_closed(), "expiry settles the approval and closes its question"
    assert replacement.row_id != expired.row_id and replacement.decision == replacement.PENDING, "the same exact request gets a fresh current approval after expiry"
    assert app.container.get(Approvals).for_action(Actor.agent(worker.session).stamp, worker.role, worker.plan_id, task.row_id, ApprovalAction.CONTRACT_CHANGE.value, replacement.request_hash).row_id == replacement.row_id, "lookup selects the replacement request"
    replacement = approvals.approve(replacement, actor)
    assert replacement.decision == replacement.APPROVED and attempt("amend contract").refusal is None, "the approved replacement passes once"
    assert attempt("amend contract").refusal == contract_change, "the approved replacement cannot pass a second time"

    assert attempt("grant access").refusal == OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.SECURITY_DECISION.value)
    security = approval_for("grant access", ApprovalAction.SECURITY_DECISION)
    with scope.environment(security.question_environment_id):
        question = app.container.get(Questions).find(security.question_id)
        approvals.answering.answer(question, "yes", Actor.agent(worker.session))
    security_wait = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.SECURITY_DECISION.value)
    assert attempt("grant access").refusal == security_wait, "an agent's positive question answer cannot approve its own action"
    assert app.container.get(Approvals).find(security.row_id).decision == security.REFUSED, "the non-user answer is recorded as refused"


def test_an_approval_is_bound_to_the_exact_tool_arguments_target_and_full_command(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "deployer", writes=True, tools=["read_files", "edit_files"], approval_required=["production_deployment"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "deployer"])
    contracts = organization.reload()
    actor = Actor.user(1)
    scope = app.container.get(Scope)
    with scope.environment(1):
        worker = app.container.get(Workers).save(Worker(name="Ada Lovelace", brief="deploy", session="bound-worker", role="deployer", contract=contracts.version), actor)
        tasks = app.container.get(Tasks)
        task = tasks.save(Task(title="release", state=TaskState.STARTED), actor)
        tasks.handover(task, Ref.build(worker), actor)
    approvals = app.container.get(RoleApprovals)
    repository = app.container.get(Approvals)
    questions = app.container.get(Questions)
    organization_data = app.container.get(OrganizationDataReader).read(Agent(environment_id=worker.environment_id, session=worker.session))
    data = FeatureData({"workers": WorkersData((), (), 0, (), Path("/w"), (), session_workers=(worker,)), "organization": organization_data})

    def call_for(tool: str, target: str):
        return Claude().call(tool, {"target": target}, frozenset(), CLASSIFIER)

    def attempt(call):
        event = ToolStarting(session=worker.session, environment_id=worker.environment_id, call=call).with_data(data)
        return RoleConduct.on_tool_starting(Ready(), event, Settings({}))

    def approval_for(call):
        request_hash, _ = ApprovalActions.identity(call)
        return repository.for_action(Actor.agent(worker.session).stamp, worker.role, worker.plan_id, task.row_id, ApprovalAction.PRODUCTION_DEPLOYMENT.value, request_hash)

    original = call_for("mcp__release__production_deployment", "production")
    altered_target = call_for("mcp__release__production_deployment", "staging")
    altered_tool = call_for("mcp__release_v2__production_deployment", "production")
    waits = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.PRODUCTION_DEPLOYMENT.value)
    assert attempt(original).refusal == waits, "a tool request waits for a user decision"
    approved = approval_for(original)
    assert approved.request_hash and '"target": "production"' in approved.request_details, "the saved grant names its exact normalized arguments and target"
    with scope.environment(approved.question_environment_id):
        question = questions.find(approved.question_id)
    assert "mcp__release__production_deployment" in question.text and '"target": "production"' in question.text, "the question gives the user the tool and target being approved"
    approvals.approve(approved, actor)
    assert attempt(altered_target).refusal == waits and attempt(altered_tool).refusal == waits, "an altered target or tool name cannot use the grant"
    assert approval_for(altered_target).row_id != approved.row_id and approval_for(altered_tool).row_id != approved.row_id, "each altered request has its own pending grant"
    assert attempt(original).refusal is None and attempt(original).refusal == waits, "the exact approved call passes once and then is refused"

    command = Claude().call("Bash", {"command": "make deploy"}, frozenset(), CLASSIFIER)
    appended = Claude().call("Bash", {"command": "make deploy && make deploy"}, frozenset(), CLASSIFIER)
    command_hash, _ = ApprovalActions.identity(command)
    appended_hash, appended_details = ApprovalActions.identity(appended)
    assert ApprovalActions.of(appended) == (ApprovalAction.PRODUCTION_DEPLOYMENT,), "both operations belong to one approval category"
    assert appended.command == "make deploy && make deploy" and appended_hash != command_hash and "make deploy && make deploy" in appended_details, "normalization retains the full appended operation in the identity and user details"
    assert attempt(command).refusal == waits, "the single deployment command asks for its own approval"
    approved_command = approval_for(command)
    approvals.approve(approved_command, actor)
    assert attempt(appended).refusal == waits, "a second same-category operation cannot use the single-command grant"
    assert approval_for(appended).request_hash == appended_hash and approval_for(appended).row_id != approved_command.row_id, "the appended command has a distinct pending request"
    assert attempt(command).refusal is None and attempt(command).refusal == waits, "the old grant remains available for one exact single-command run"


def test_a_solo_role_rejects_an_excluded_mcp_tool_without_spending_approval_and_allows_its_tool_once(app, tmp_path):
    from journal.features.organization.states.role_work import RoleWork
    from journal.features.plans.plans_part import PlansPart
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.plans.support.started_plan import StartedPlan
    from journal.features.organization.support.role_approvals import RoleApprovalContext

    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "deployer", writes=True, tools=["read_files", "edit_files", "run_tests"], approval_required=["production_deployment"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "deployer"])
    contracts = organization.reload()
    scope = app.container.get(Scope)
    with scope.environment(1):
        task = app.container.get(Tasks).save(Task(title="release", state=TaskState.STARTED), Actor.user(1))
    started = StartedPlan(plan_id=41, next_task=task.row_id, started_task=task.row_id, started_task_briefing="", recent_tasks=(task.row_id,), remaining_tasks=1,
                          checkpoint_pause=False, checkpoint_phase=0, testing="")
    data = FeatureData({"organization": app.container.get(OrganizationDataReader).read(Agent(environment_id=1, session="solo-plan")), PlansPart.name: PlansData(approved=(41,), started=started)})
    state = RoleWork(role="deployer", version=contracts.version)

    def attempt(call):
        event = ToolStarting(session="solo-plan", environment_id=1, call=call).with_data(data)
        with scope.environment(1):
            return state.on_tool_starting(event, Settings({}))

    role = contracts.role("deployer")
    context = RoleApprovalContext("solo-plan", "deployer", 41, task.row_id, 1)
    approvals = app.container.get(RoleApprovals)
    repository = app.container.get(Approvals)
    waits = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.PRODUCTION_DEPLOYMENT.value)

    excluded = Claude().call("mcp__release__production_deployment", {"target": "production"}, frozenset(), CLASSIFIER)
    excluded_approval = approvals.request(context, ApprovalAction.PRODUCTION_DEPLOYMENT, excluded)
    assert excluded_approval and approvals.approve(excluded_approval, Actor.user(1)).decision == excluded_approval.APPROVED
    tool_refusal = OrganizationNudges.ROLE_TOOL_REFUSED.create(role=role.title, tool=excluded.tool, tools=ToolIds().words(role.tools))
    assert attempt(excluded).refusal == tool_refusal, "a user grant does not add an excluded MCP tool to a solo Role"
    excluded_hash, _ = ApprovalActions.identity(excluded)
    still_approved = repository.for_action(Actor.agent("solo-plan").stamp, "deployer", 41, task.row_id, ApprovalAction.PRODUCTION_DEPLOYMENT.value, excluded_hash)
    assert still_approved.decision == still_approved.APPROVED and still_approved.used_at is None, "tool refusal does not spend the grant"

    call = Claude().call("Bash", {"command": "make deploy"}, frozenset(), CLASSIFIER)
    assert attempt(call).refusal == waits, "a permitted tool still asks before running an approval-required action"
    request_hash, _ = ApprovalActions.identity(call)
    approved = repository.for_action(Actor.agent("solo-plan").stamp, "deployer", 41, task.row_id, ApprovalAction.PRODUCTION_DEPLOYMENT.value, request_hash)
    assert approved and approvals.approve(approved, Actor.user(1)).decision == approved.APPROVED
    assert attempt(call).refusal is None and attempt(call).refusal == waits, "the permitted tool consumes the approval on exactly one tool start"


def test_a_domain_carries_its_icon_and_its_boards_phase_names_and_a_board_with_another_key_is_refused(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    assert organization.contracts().domain("alpha").icon == "🧪" and organization.contracts().domain("alpha").board.done == "Done", "a domain with no [board] has the plain phase names"
    fixture.domain("alpha", roles=["scout", "builder"], board={"in_progress": "Active", "done": "Completed"})
    board = organization.reload().domain("alpha").board
    assert (board.planned, board.in_progress, board.in_review, board.done) == ("Planned", "Active", "In review", "Completed"), "the names the domain gives, the plain ones for the rest"
    fixture.domain("alpha", roles=["scout", "builder"], board={"finished": "Closed", "done": ""})
    contracts = organization.reload()
    assert contracts.domain("alpha") is None and len([problem for problem in contracts.problems if problem.path == "domains/alpha/domain.toml"]) == 2, "an unknown phase and an empty name are each a problem and the domain is left out"


REAL_FOLDER = __import__("os").environ.get("JOURNAL_ORGANIZATION_FOLDER", "")


@pytest.mark.skipif(not REAL_FOLDER, reason="JOURNAL_ORGANIZATION_FOLDER names no agentic-organization folder to read")
def test_the_real_organization_folder_loads_with_no_problems(app):
    from collections import Counter
    from journal.features.organization.support.organization import Organization
    from tests.user_settings import user_set
    user_set(app, "workers.organization_folder", REAL_FOLDER)
    contracts = app.container.get(Organization).reload()
    assert [(problem.path, problem.rule, problem.message) for problem in contracts.problems] == []
    assert len(contracts.domains) == 13 and Counter(role.cardinality for role in contracts.roles) == {Cardinality.JOURNAL: 24, Cardinality.PLAN: 18, Cardinality.MANY: 8}


def test_openrig_usage_estimates_are_native_session_deltas_and_subscription_windows_stay_separate(tmp_path):
    from journal.config import Config
    from journal.features.organization.support.usage_ledger import UsageLedger

    ledger = UsageLedger(Config.rooted(tmp_path), stale_after_seconds=60)
    assert ledger.estimate(3, 100).status == "missing" and ledger.estimate(3, 100).amount_usd is None
    assert ledger.estimate(4, 100, 2).coverage == "0 of 2 seats observed"
    first = ledger.observe(3, "builder@release", "native-a", 2.5, 100, 2)
    next_turn = ledger.observe(3, "builder@release", "native-a", 3.0, 110, 2)
    reset = ledger.observe(3, "builder@release", "native-a", 0.2, 120, 2)
    new_session = ledger.observe(3, "builder@release", "native-b", 0.4, 130, 2)
    assert first.amount_usd == 2.5 and next_turn.amount_usd == 3.0 and reset.amount_usd == 3.2 and new_session.amount_usd == 3.6
    assert new_session.source == "OpenRig native-session estimate" and new_session.coverage == "1 of 2 seats observed" and new_session.freshness == "fresh" and new_session.status == "partial"
    ledger.observe(4, "older-seat", "native-c", 1.0, 100, 2)
    ledger.observe(4, "newer-seat", "native-d", 1.0, 190, 2)
    assert ledger.estimate(4, 200, 2).freshness == "stale", "one stale seat makes the plan estimate stale even if another seat is recent"
    ledger.record_subscription_limits({"five_hour": {"used_percentage": 40, "resets_at": 200}}, "Claude Code status line", "5h", 130)
    limits = ledger.subscription_limits(140)
    assert limits.status == "available" and limits.coverage == "account-wide subscription windows" and limits.limits["five_hour"]["used_percentage"] == 40
    ledger.record_subscription_limits(None, "Codex journal status files", "account-wide subscription windows", 150)
    missing_limits = ledger.subscription_limits(151)
    assert missing_limits.status == "missing" and missing_limits.freshness == "fresh" and missing_limits.source == "Codex journal status files"
    assert ledger.estimate(3, 1000).status == "stale" and ledger.subscription_limits(1000).status == "stale"


def test_worker_caps_keep_account_seat_capacity_and_plan_estimates_distinct():
    from journal.features.organization.support.caps import Caps
    from journal.features.organization.support.usage_ledger import UsageEstimate

    class Settings:
        @staticmethod
        def integer(option):
            return 2

        @staticmethod
        def decimal(option):
            return 5.0

    caps = Caps(Settings())
    assert caps.seats(1).allowed and caps.seats(2).status == "full"
    missing = UsageEstimate(3, None, "OpenRig native-session estimate", None, None, "0 of unknown seats observed", "missing", "missing")
    over = UsageEstimate(3, 5.0, "OpenRig native-session estimate", 10, 20, "1 of 1 seats observed", "fresh", "estimated")
    partial = UsageEstimate(3, 6.0, "OpenRig native-session estimate", 10, 20, "1 of 2 seats observed", "fresh", "estimated", 1, 2)
    assert caps.plan_cost(missing).status == "unknown" and not caps.plan_cost(missing).allowed
    assert caps.plan_cost(over).status == "exceeded" and "estimated OpenRig usage" in caps.plan_cost(over).reason
    assert caps.plan_cost(partial).status == "unknown" and "1 of 2 seats" in caps.plan_cost(partial).reason


def test_a_followup_codex_job_uses_the_existing_openrig_session_while_its_monitor_is_winding_down(monkeypatch):
    from contextlib import nullcontext
    from types import SimpleNamespace
    import threading
    from journal.features.organization.support import seat_runner as seat_runner_module
    from journal.features.organization.support.seat_runner import SeatRunner
    from journal.features.organization.support.seat_runtime import SeatSession
    from journal.models.worker import Worker
    from journal.support.actor import Actor
    from journal.support.agent_token import AgentToken

    class CapturedThread:
        def __init__(self, *, target, args, name, daemon):
            self.target, self.args, self.name, self.daemon = target, args, name, daemon
            threads.append(self)

        def start(self):
            pass

    threads = []
    monkeypatch.setattr(seat_runner_module.threading, "Thread", CapturedThread)
    prior_job = Worker(id=8, name="Ada Lovelace", role="builder", plan_id=8, contract="contract", provider="codex", model="gpt-6-luna", resume="thread-9", pid=0).moved("dispatched", 10)
    worker = prior_job.moved("sent a job", 20)
    runner = object.__new__(SeatRunner)
    runner._guard = threading.Lock()
    runner._active = {worker.id}
    from journal.features.organization.support.seat_runner import SeatJobIdentity
    prior_identity = SeatJobIdentity.from_worker(prior_job)
    identity = SeatJobIdentity.from_worker(worker)
    runner._active_jobs = {worker.id: prior_identity}
    runner.start(worker, Actor.system(), "next job", lambda *args: None)

    assert len(threads) == 1 and threads[0].target == runner.send_existing and threads[0].args[1] == identity and threads[0].args[3] == "next job"

    member = SimpleNamespace(provider="codex", model="gpt-6-luna", openrig_version="0.7.5", target="alpha-builder@release")
    sent, saved = [], []
    runner.scope = SimpleNamespace(environment=lambda _environment: nullcontext())
    runner.member = lambda _worker: member
    runner.runtime = SimpleNamespace(
        check_version=lambda _version: "0.7.5",
        worker_token=lambda *_args: AgentToken("seat-token"),
        session=lambda _member, native: SeatSession(91, native, "running", 25),
        send=lambda _member, prompt: sent.append(prompt),
    )
    runner.environments = SimpleNamespace(find=lambda _environment: SimpleNamespace(name="development"))
    role = SimpleNamespace(models=SimpleNamespace(for_provider=lambda _provider: "gpt-6-luna"))
    runner.organization = SimpleNamespace(at=lambda _contract: SimpleNamespace(role=lambda _role: role))
    runner.workers = SimpleNamespace(find=lambda _row: worker, save=lambda current, _actor: saved.append(current) or current)
    runner.time_source = SimpleNamespace(seconds=lambda: 30)
    runner.monitor = lambda *args: None
    monkeypatch.setattr("journal.features.organization.support.seat_runner.ProcessCheck.is_running", lambda _pid: True)
    runner.send_existing(worker, identity, Actor.system(), "next job", lambda *args: None)

    assert sent == ["next job"] and saved[-1].pid == 91 and saved[-1].resume == "thread-9" and saved[-1].token_hash == AgentToken("seat-token").digest()


def test_a_codex_job_runs_on_its_selected_role_seat_and_saves_the_native_session(monkeypatch):
    from types import SimpleNamespace
    from journal.features.organization.support.seat_runner import SeatRunner
    from journal.features.organization.support.seat_runtime import SeatSession
    from journal.models.worker import Worker
    from journal.support.actor import Actor
    from journal.support.agent_token import AgentToken

    worker = Worker(id=9, name="Ada Lovelace", role="builder", plan_id=8, contract="contract", provider="codex", model="gpt-6-luna", resume="thread-9").moved("dispatched", 10)
    member = SimpleNamespace(provider="codex", model="gpt-6-luna", openrig_version="0.7.5", target="alpha-builder@release")
    sent, saved, monitored = [], [], []
    runner = object.__new__(SeatRunner)
    runner.member = lambda _worker: member
    runner.runtime = SimpleNamespace(
        check_version=lambda _version: "0.7.5",
        worker_token=lambda *_args: AgentToken("seat-token"),
        session=lambda _member, native: SeatSession(91, native, "running", 25),
        send=lambda _member, prompt: sent.append(prompt),
    )
    runner.environments = SimpleNamespace(find=lambda _environment: SimpleNamespace(name="development"))
    role = SimpleNamespace(models=SimpleNamespace(for_provider=lambda provider: "gpt-6-luna" if provider == "codex" else ""))
    runner.organization = SimpleNamespace(at=lambda _contract: SimpleNamespace(role=lambda _role: role))
    runner.capacity_available = lambda _worker: True
    runner.workers = SimpleNamespace(find=lambda _row: worker, save=lambda current, _actor: saved.append(current) or current)
    runner.time_source = SimpleNamespace(seconds=lambda: 30)
    runner.monitor = lambda *args: monitored.append(args)
    monkeypatch.setattr("journal.features.organization.support.seat_runner.ProcessCheck.is_running", lambda _pid: True)

    from journal.features.organization.support.seat_runner import SeatJobIdentity
    identity = SeatJobIdentity.from_worker(worker)
    runner.run(worker, identity, Actor.system(), "write the patch", lambda *args: None)

    assert sent == ["write the patch"] and saved[-1].pid == 91 and saved[-1].session == "thread-9" and saved[-1].resume == "thread-9"
    assert saved[-1].token_hash == AgentToken("seat-token").digest() and monitored[0][1] == identity and monitored[0][3] == "thread-9"


def test_seat_recovery_attaches_to_an_existing_process_without_launching_a_new_agent(monkeypatch):
    import threading
    from journal.features.organization.support import seat_runner as seat_runner_module
    from journal.features.organization.support.seat_runner import SeatRunner
    from journal.models.worker import Worker
    from journal.support.actor import Actor

    class CapturedThread:
        def __init__(self, *, target, args, name, daemon):
            self.target, self.args, self.name, self.daemon = target, args, name, daemon
            threads.append(self)

        def start(self):
            pass

    threads = []
    monkeypatch.setattr(seat_runner_module.threading, "Thread", CapturedThread)
    worker = Worker(id=10, name="Ada Lovelace", role="builder", plan_id=8, provider="codex", model="gpt-6-luna", pid=91, resume="thread-9").moved("dispatched", 10)
    runner = object.__new__(SeatRunner)
    runner._guard = threading.Lock()
    runner._active = set()
    runner._active_jobs = {}
    runner.recover(worker, Actor.system(), "do not resend this job", lambda *args: None)

    assert len(threads) == 1 and threads[0].target == runner.monitor_existing and threads[0].args[0] == worker


def test_seat_monitor_finishes_on_clockout_or_when_its_queue_item_is_done(monkeypatch):
    import threading
    from types import SimpleNamespace
    from journal.features.organization.support import seat_runner as seat_runner_module
    from journal.features.organization.support.seat_runner import SeatRunner
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.support.actor import Actor

    monkeypatch.setattr(seat_runner_module.time, "sleep", lambda _seconds: None)

    def monitored(current, holders, finished):
        runner = object.__new__(SeatRunner)
        runner._guard = threading.Lock()
        runner._finishing = set()
        runner.workers = SimpleNamespace(find=lambda _row: current)
        runner.tasks = SimpleNamespace(holder_task_ids=lambda _ref: holders, finished_task_ids=lambda _ref: finished)
        runner.time_source = SimpleNamespace(seconds=lambda: 20)
        usage = []
        runner.record_usage = lambda *args: usage.append(args)
        ended = []
        worker = Worker(id=11, name="Ada Lovelace", role="builder", plan_id=8, state=WorkerState.DISPATCHED, pid=91).moved("dispatched", 10)
        from journal.features.organization.support.seat_runner import SeatJobIdentity
        identity = SeatJobIdentity.from_worker(worker)
        runner.monitor(worker, identity, None, "thread-9", Actor.system(), lambda *args: ended.append(args), 10)
        return ended, usage

    dispatched = Worker(id=11, name="Ada Lovelace", state=WorkerState.DISPATCHED, pid=91).moved("dispatched", 10)
    clocked_out, clockout_usage = monitored(dispatched.reported(20, 1), (), ())
    queue_done, queue_usage = monitored(dispatched, (), (42,))

    assert len(clocked_out) == 1 and clockout_usage, "clockout ends the active job after recording usage"
    assert len(queue_done) == 1 and not queue_usage, "a finished queue item ends its seat job"


def test_old_seat_completion_cannot_finish_or_unmonitor_a_followup_generation(monkeypatch):
    from threading import Event, Lock, Thread
    from types import SimpleNamespace
    from journal.events.rows.worker_reused import WorkerReused
    from journal.features.organization.support import seat_runner as seat_runner_module
    from journal.features.organization.support.seat_runner import SeatJobIdentity, SeatRunner
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.models.worker import Worker
    from journal.support.actor import Actor

    monkeypatch.setattr(seat_runner_module.time, "sleep", lambda _seconds: None)
    old = Worker(id=16, name="Ada Lovelace", pid=91).moved("dispatched", 10)
    old_identity = SeatJobIdentity.from_worker(old)
    followup = old.resumed("write the follow-up", 20, WorkerReused, "sent a job")
    followup_identity = SeatJobIdentity.from_worker(followup)
    current = old
    runner = object.__new__(SeatRunner)
    runner._guard = Lock()
    runner._active = {old.id}
    runner._active_jobs = {old.id: old_identity}
    runner._finishing = set()
    runner.workers = SimpleNamespace(find=lambda _row: current)
    runner.tasks = SimpleNamespace(holder_task_ids=lambda _ref: (), finished_task_ids=lambda _ref: (42,))
    runner.time_source = SimpleNamespace(seconds=lambda: 30)
    entered, resume, failures = Event(), Event(), []
    worker_runner = object.__new__(WorkerRunner)
    worker_runner._locks = {}
    worker_runner._locks_lock = Lock()
    worker_runner.workers = runner.workers
    worker_runner.seats = SimpleNamespace(preserve=lambda *_args: failures.append("stale preserve"))

    def old_completion(worker, identity, code, actor):
        entered.set()
        if not resume.wait(2):
            failures.append("completion was not resumed")
            return
        worker_runner.finish_seat(worker, identity, code, actor)

    def monitor_old_job():
        try:
            runner.monitor(old, old_identity, None, "thread-9", Actor.system(), old_completion, 10)
        except BaseException as failure:
            failures.append(str(failure))
        finally:
            runner.release(old_identity)

    monitor = Thread(target=monitor_old_job)
    monitor.start()
    assert entered.wait(2), "the old monitor reached its pending completion callback"
    current = followup
    with runner._guard:
        runner._active_jobs[old.id] = followup_identity
    resume.set()
    monitor.join(2)

    assert not monitor.is_alive() and not failures
    assert current == followup and current.brief == "write the follow-up"
    assert runner._active == {old.id} and runner._active_jobs[old.id] == followup_identity


def test_seat_monitor_requires_fresh_openrig_idle_evidence_after_job_start(monkeypatch):
    import threading
    from types import SimpleNamespace
    from journal.features.organization.support.seat_runner import SeatRunner
    from journal.features.organization.support.seat_runtime import SeatRuntime, SeatSession
    from journal.models.worker import Worker
    from journal.support.actor import Actor

    monkeypatch.setattr("journal.features.organization.support.seat_runner.ProcessCheck.is_running", lambda _pid: True)
    member = SimpleNamespace(provider="codex", model="gpt-6-luna", openrig_version="0.7.5", target="alpha-builder@release")

    def check(sampled_at):
        worker = Worker(id=17, name="Ada Lovelace", pid=91).moved("dispatched", 100)
        runner = object.__new__(SeatRunner)
        runner._guard = threading.Lock()
        runner._finishing = set()
        runner.workers = SimpleNamespace(find=lambda _row: worker)
        runner.settings = SimpleNamespace(decimal=lambda _option: 0)
        runner.time_source = SimpleNamespace(seconds=lambda: 120)
        runner.member = lambda _worker: member
        node_status = {"nodes": [{"name": member.target, "agentActivity": {
            "state": "idle", "reason": "no recent agent event", "evidenceSource": "native_hook",
            "sampledAt": sampled_at, "evidence": None,
        }}]}
        activity, updated = SeatRuntime.activity_status(node_status)
        runner.runtime = SimpleNamespace(
            session=lambda *_args: SeatSession(91, "thread-9", "running", updated, activity),
        )
        ended = []
        finished = runner.is_finished(worker, Actor.system(), lambda *args: ended.append(args))
        return finished, ended

    stale_finished, stale_callbacks = check("1970-01-01T00:01:39Z")
    fresh_finished, fresh_callbacks = check("1970-01-01T00:01:41Z")

    assert not stale_finished and not stale_callbacks, "idle evidence sampled before dispatch cannot end a delivered-late job"
    assert fresh_finished and len(fresh_callbacks) == 1, "a fresh idle sample can end a job after its grace period"


def test_seat_runtime_uses_the_existing_rig_spec_and_pinned_openrig_version(tmp_path, monkeypatch):
    import json
    import os
    import shutil
    import subprocess
    from journal.config import Config
    from journal.features.organization.support.seat_runtime import SeatRuntime
    from journal.features.workers.organization_options import OrganizationOptions

    config = Config.rooted(tmp_path)
    spec = config.home / "runtime" / "rigs" / "release" / "rig.yaml"
    spec.parent.mkdir(parents=True)
    spec.write_text(json.dumps({"pods": [{"id": "alpha", "members": [{
        "id": "builder", "agent_ref": "local:agents/alpha-builder", "runtime": "codex",
        "model": "gpt-6-luna", "env": {"JOURNAL_ACTOR": "worker:7", "JOURNAL_ACTOR_TOKEN": "seat-token",
        "JOURNAL_ENV": "development", "JOURNAL_ROOT": str(config.root), "PATH": str(config.home / "bin") + os.pathsep + "/usr/bin",
        "AGENT_JOURNAL_ACTIVE": "1", "JOURNAL_AGENT_SHELL": "1"},
        "codex_permissions": {"sandbox": "workspace-write", "approval": "never"},
    }]}]}))
    agent = spec.parent / "agents" / "alpha-builder"
    agent.mkdir(parents=True)
    (agent / "agent.yaml").write_text(json.dumps({"resources": {"runtime_resources": [{"id": "journal-hooks", "path": "runtime/journal-hooks.json", "runtime": "codex"}],
        "skills": [{"id": "journal", "path": "skills/journal"}]},
        "profiles": {"default": {"uses": {"skills": ["journal"]}}}}))
    (agent / "runtime").mkdir()
    (agent / "runtime" / "journal-hooks.json").write_text("{}")

    class Settings:
        @staticmethod
        def option(option):
            return "0.7.5" if option == OrganizationOptions.OPENRIG_VERSION else ""

    calls = []

    def execute(arguments, **kwargs):
        calls.append(arguments)
        if arguments[1:3] == ["seat", "status"]:
            return subprocess.CompletedProcess(arguments, 0, json.dumps({"sessionStatus": "running", "threadId": "thread-9", "process": {"pid": 91}}), "")
        if arguments[1:2] == ["ps"]:
            return subprocess.CompletedProcess(arguments, 0, json.dumps({"nodes": [{
                "name": "alpha-builder@release", "threadId": "thread-9", "pid": 91,
                "agentActivity": {"state": "running", "reason": "agent is working", "evidenceSource": "native_hook",
                                  "sampledAt": "2026-10-29T15:00:00Z", "evidence": None},
            }]}), "")
        if arguments[1:] == ["--version"]:
            return subprocess.CompletedProcess(arguments, 0, "rig version 0.7.5\n", "")
        if arguments[1:2] == ["send"]:
            assert arguments == ["rig", "send", "alpha-builder@release", "write the patch", "--json"], "0.7.5 treats --rig as fan-out; a seat send has only the bare seat and text positionals"
            return subprocess.CompletedProcess(arguments, 0, "{}", "")
        return subprocess.CompletedProcess(arguments, 0, "{}", "")

    monkeypatch.setattr(shutil, "which", lambda program: "/usr/bin/rig")
    runtime = SeatRuntime(config, Settings(), execute)
    member = runtime.member("release", "alpha", "builder", "codex")
    token = runtime.worker_token(member, "codex", "gpt-6-luna", "worker:7", "development")
    assert (member.logical_id, member.target, member.provider, member.model, member.runtime) == ("alpha.builder", "alpha-builder@release", "codex", "gpt-6-luna", "codex")
    assert token.text == "seat-token"
    assert runtime.check_version() == "0.7.5"
    session = runtime.session(member)
    runtime.send(member, "write the patch")
    assert (session.pid, session.session, session.status) == (91, "thread-9", "running")
    assert session.activity_status == "running" and session.status_updated_at > 1_700_000_000
    assert ["rig", "ps", "--nodes", "--full", "--json", "--rig", "release"] in calls
    assert ["rig", "send", member.target, "write the patch", "--json"] in calls


def _seat_failure_world(app, tmp_path):
    from journal.events.bus import Bus
    from journal.events.listener import Listener
    from journal.events.rows.role_escalated import RoleEscalated
    from journal.models.agent import Agent
    from journal.models.plan import Plan
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.repositories.agents import Agents
    from journal.repositories.domain_rows import DomainRows
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
    agents, domains, plans, workers, scope = (app.container.get(kind) for kind in (Agents, DomainRows, Plans, Workers, Scope))
    actor = Actor.system()
    with scope.environment(1):
        plan = plans.save(Plan(environment_id=1, title="alpha build"), actor)
        domain = agents.save(Agent(environment_id=1, session="domain-alpha", provider="codex", state="idle"), actor)
        domains.agent_linked("alpha", domain, actor)
        worker = workers.save(Worker(
            environment_id=1, name="Ada Lovelace", brief="patch", role="builder", plan_id=plan.id,
            profile="journal-senior", dispatcher="s1", provider="codex", model="gpt-6-luna",
            state=WorkerState.DISPATCHED, pid=91, session="thread-9", token_hash="seat-token",
        ).moved("dispatched", 100), actor)
    return worker, workers, escalated, actor


def _seat_failure_finisher(workers, tmp_path):
    from threading import Lock
    from types import SimpleNamespace
    from journal.features.workers.support.worker_runner import WorkerRunner

    runner = object.__new__(WorkerRunner)
    runner._locks = {}
    runner._locks_lock = Lock()
    runner.workers = workers
    runner.seats = SimpleNamespace(preserve=lambda *_args: None)
    runner.config = SimpleNamespace(home=tmp_path)
    runner.settings = SimpleNamespace(decimal=lambda _option: 1)
    runner.time_source = SimpleNamespace(seconds=lambda: 200)
    return runner


def _seat_monitor(worker, workers, runtime, now, timeout_minutes):
    from threading import Lock
    from types import SimpleNamespace
    from journal.features.organization.support.seat_runner import SeatRunner

    runner = object.__new__(SeatRunner)
    runner._guard = Lock()
    runner._finishing = set()
    runner.workers = workers
    runner.tasks = SimpleNamespace(holder_task_ids=lambda _ref: (), finished_task_ids=lambda _ref: ())
    runner.time_source = SimpleNamespace(seconds=lambda: now)
    runner.settings = SimpleNamespace(decimal=lambda _option: timeout_minutes)
    runner.runtime = runtime
    return runner


def test_a_dead_seat_requeues_its_job_and_escalates_to_its_domain_agent(app, tmp_path, monkeypatch):
    from types import SimpleNamespace
    from journal.features.organization.support import seat_runner as seat_runner_module
    from journal.features.organization.support.seat_runner import SeatJobIdentity
    from journal.models.worker_state import WorkerState

    monkeypatch.setattr(seat_runner_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(seat_runner_module.ProcessCheck, "is_running", lambda _pid: False)
    worker, workers, escalated, actor = _seat_failure_world(app, tmp_path)
    finisher = _seat_failure_finisher(workers, tmp_path)
    seat = _seat_monitor(worker, workers, SimpleNamespace(session=lambda *_args: None), 101, 0)
    identity = SeatJobIdentity.from_worker(worker)

    seat.monitor(worker, identity, SimpleNamespace(target="alpha-builder@release"), worker.resume,
                 actor, finisher.finish_seat, worker.job_start_time())

    current = workers.find(worker.row_id)
    assert current.state == WorkerState.UNFINISHED and "ended without clocking out" in current.run_end
    assert len(escalated) == 1 and escalated[0][0] == "domain-alpha" and "ended without clocking out" in escalated[0][1]


def test_a_stuck_seat_times_out_its_job_and_escalates_to_its_domain_agent(app, tmp_path, monkeypatch):
    from types import SimpleNamespace
    from journal.features.organization.support import seat_runner as seat_runner_module
    from journal.features.organization.support.seat_runner import SeatJobIdentity
    from journal.models.worker_state import WorkerState

    monkeypatch.setattr(seat_runner_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(seat_runner_module.ProcessCheck, "is_running", lambda _pid: True)
    worker, workers, escalated, actor = _seat_failure_world(app, tmp_path)
    finisher = _seat_failure_finisher(workers, tmp_path)
    stopped = []
    runtime = SimpleNamespace(
        session=lambda *_args: SimpleNamespace(pid=91, session="thread-9", activity_status="busy", status_updated_at=100),
        stop=lambda target, reason: stopped.append((target, reason)),
    )
    seat = _seat_monitor(worker, workers, runtime, 0, 1)
    samples = iter((100.5, 161))
    seat.time_source = SimpleNamespace(seconds=lambda: next(samples))
    seat.record_usage = lambda *_args: None
    identity = SeatJobIdentity.from_worker(worker)

    seat.monitor(worker, identity, SimpleNamespace(target="alpha-builder@release"), worker.resume,
                 actor, finisher.finish_seat, worker.job_start_time())

    current = workers.find(worker.row_id)
    assert stopped and current.state == WorkerState.UNFINISHED and "without ending" in current.run_end
    assert len(escalated) == 1 and escalated[0][0] == "domain-alpha" and "without ending" in escalated[0][1]


def test_an_unreachable_openrig_times_out_and_requeues_without_leaving_a_monitored_job(app, tmp_path, monkeypatch):
    import subprocess
    from threading import Lock
    from contextlib import nullcontext
    from types import SimpleNamespace
    from journal.features.organization.support import seat_runtime as seat_runtime_module
    from journal.features.organization.support.seat_runner import SeatJobIdentity, SeatRunner
    from journal.features.organization.support.seat_runtime import SeatRuntime
    from journal.models.worker_state import WorkerState

    worker, workers, escalated, actor = _seat_failure_world(app, tmp_path)
    finisher = _seat_failure_finisher(workers, tmp_path)
    calls = []

    def unreachable(arguments, **kwargs):
        calls.append((arguments, kwargs))
        raise subprocess.TimeoutExpired(arguments, kwargs["timeout"])

    monkeypatch.setattr(seat_runtime_module.shutil, "which", lambda _program: "/usr/bin/rig")
    runtime = SeatRuntime(SimpleNamespace(home=tmp_path), SimpleNamespace(option=lambda _option: ""), unreachable)
    identity = SeatJobIdentity.from_worker(worker)
    seat = object.__new__(SeatRunner)
    seat._guard = Lock()
    seat._finishing = set()
    seat._active = {worker.id}
    seat._active_jobs = {worker.id: identity}
    seat.workers = workers
    seat.runtime = runtime
    seat.config = SimpleNamespace(home=tmp_path)
    seat.scope = SimpleNamespace(environment=lambda _environment: nullcontext())
    seat.member = lambda _worker: SimpleNamespace(openrig_version="0.7.5")

    seat.monitor_existing(worker, identity, actor, finisher.finish_seat)

    current = workers.find(worker.row_id)
    assert current.state == WorkerState.UNFINISHED and "seat failed:" in current.run_end
    assert len(escalated) == 1 and escalated[0][0] == "domain-alpha" and "OpenRig --version failed" in escalated[0][1]
    assert calls[0][0] == ["rig", "--version"] and calls[0][1]["timeout"] == 30 and not seat._active


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

        assert send("Ida Rhodes", "--role", "builder").code == 0 and send("Rosalind Franklin", "--role", "builder").code == 0 and len(started) == 3, "a many Role starts an instance for each job"

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


def test_a_seat_on_a_model_other_than_its_roles_contract_names_is_caught_and_one_on_it_is_not():
    from journal.features.organization.support.seat_model_guard import SeatModelGuard
    role = a_role(models=RoleModels("sonnet", "gpt-6-luna", "max"))
    assert SeatModelGuard.mismatch(role, "claude", "sonnet") == "" and SeatModelGuard.mismatch(role, "claude", "claude-sonnet-5-5") == "", "the contract's model, whole or in a full name, is right"
    assert SeatModelGuard.mismatch(role, "codex", "gpt-6-luna") == "", "and so on Codex"
    wrong = SeatModelGuard.mismatch(role, "claude", "opus")
    assert "runs on opus" in wrong and "names sonnet" in wrong and wrong.endswith("restart it on sonnet"), "a seat on another model is named with the model to restart it on"
    assert "no model" in SeatModelGuard.mismatch(role, "codex", ""), "a seat with no observed model is not trusted"


def test_a_codex_role_job_starts_with_the_reasoning_effort_its_contract_names_and_a_claude_one_with_none(app, tmp_path, monkeypatch):
    from journal.features.organization.support.role_boot import RoleBoot
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.providers.codex import Codex
    from journal.supervisor_link import SupervisorLink
    from journal.support.caller import Caller
    from tests.test_features import hook
    from tests.worker_dispatch import dispatched
    started = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: None)
    monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: started.append(worker))
    fixture, organization = loaded(app, tmp_path)
    fixture.role("beta", "porter", cardinality="many", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.domain("beta", roles=["keeper", "porter"])
    organization.reload()
    agent = Caller.agent("main", "s1", "claude")
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], agent)
    for provider in ("codex", "claude"):
        sent = dispatched(console, [f"Ada {provider}", "the job", "--changes", "the files of its task", "--role", "porter", "--provider", provider], agent)
        assert sent.code == 0, sent.error
    from journal.repositories.scope import Scope
    with app.container.get(Scope).environment(1):
        roles, runner = app.container.get(RoleBoot), app.container.get(WorkerRunner)
        codex, claude = started
        assert roles.effort(codex) == "max" and roles.effort(claude) == "", "only a Codex worker is given its Role's effort"
        command = Codex().worker_command(runner.instructed(codex), codex.model, codex.resume, codex.session, roles.effort(codex))
        assert command[-3:-1] == ["-c", "model_reasoning_effort=max"] and command[-1] == runner.instructed(codex), "the effort is set with -c before the brief"
        assert "model_reasoning_effort" not in " ".join(Codex().worker_command("brief", "gpt-6-luna", "", "")), "no effort named, none set"


def test_the_queue_of_a_journal_role_keeps_its_order_across_a_restart_and_hands_no_job_to_a_second_instance(tmp_path, monkeypatch):
    from journal.config import Config
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.models.support.ref import Ref
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.supervisor_link import SupervisorLink
    from journal.support.caller import Caller
    from tests.main_journal import main_journal
    from tests.organization_fixture import OrganizationFixture
    from tests.test_features import hook
    from tests.user_settings import user_set
    from tests.worker_dispatch import dispatched
    started = []
    monkeypatch.setattr(Config, "status_home", property(lambda self: tmp_path / "status"))
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: None)
    monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: started.append(worker))
    fixture = OrganizationFixture(tmp_path / "organization").write()
    fixture.role("alpha", "steward", cardinality="journal", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "steward"])
    agent = Caller.agent("main", "s1", "claude")
    send = lambda console, name: dispatched(console, [name, f"the job of {name}", "--changes", "the files of its task", "--role", "steward"], agent)
    first = main_journal(Config(tmp_path, port=0))
    first.runtime().start()
    user_set(first, "workers.organization_folder", str(fixture.root))
    hook(first, "SessionStart")
    first.console().run(["environment", "overview"], agent)
    user_set(first, "workers.testing", "Hand the tests over")
    sent = [send(first.console(), name) for name in ("Ada Lovelace", "Grace Hopper", "Ida Rhodes")]
    assert [outcome.code for outcome in sent] == [0, 0, 0] and len(started) == 1, ([outcome.error for outcome in sent], "one instance, the other two jobs queued on it")
    first.runtime().stop()
    second = main_journal(Config(tmp_path, port=0))
    second.runtime().start()
    try:
        with second.container.get(Scope).environment(1):
            [instance] = second.container.get(Workers).role_instances("steward")
            queued = lambda: [task.id for task in second.container.get(Tasks).queue(Ref.build(instance))]
            assert queued() == [2, 3], "after the restart the queue keeps its order"
            assert send(second.console(), "Edith Clarke").code == 0 and len(started) == 1 and len(second.container.get(Workers).role_instances("steward")) == 1, "a job sent after the restart joins the one instance"
            assert queued() == [2, 3, 4] and len(set(queued())) == len(queued()), "at the end of the queue, and no job twice"
    finally:
        second.runtime().stop()


def test_the_organization_is_served_in_one_answer_and_each_domains_counts_are_a_row_that_follows_its_instances_queues_and_active_plans(app, tmp_path):
    from datetime import datetime, timezone
    from journal.models.link import Link
    from journal.models.plan import Plan
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.domain_counts import DomainCounts
    from journal.repositories.domain_rows import DomainRows
    from journal.repositories.links import Links
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import PLAN_LINK, Tasks
    from journal.repositories.workers import Workers
    from journal.support.actor import Actor
    from tests.in_process import answered, got
    fixture, organization = loaded(app, tmp_path)
    git = lambda *args: InnerRepositories.git(fixture.root, "-c", "user.name=Test", "-c", "user.email=test@example.com", *args)
    assert git("init", "-q").returncode == 0
    git("add", "-A")
    assert git("commit", "-q", "-m", "organization").returncode == 0
    commit = git("rev-parse", "HEAD").stdout.strip()
    organization.reload()
    tasks, workers, plans, links, counts = (app.container.get(kind) for kind in (Tasks, Workers, Plans, Links, DomainCounts))
    actor, now = Actor.system(), datetime.now(timezone.utc)
    env = {"X-Journal-Env": "main"}
    with app.container.get(Scope).environment(1):
        plan = plans.save(Plan(environment_id=1, title="the floors"), actor)
        built, looked, kept = (tasks.save(Task(environment_id=1, title=title, brief=f"{title} reads"), actor) for title in ("the build", "the lookup", "the contract"))
        for task in (built, looked, kept):
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
        assert counts.all_matching() == [], "no count until a task is handed to a Role"
        builder = workers.save(Worker(environment_id=1, name="Mr. Brunel", brief="b", profile="journal-senior", role="builder", plan_id=plan.id), actor)
        keeper = workers.save(Worker(environment_id=1, name="Ms. Hopper", brief="b", profile="journal-senior", role="keeper", plan_id=plan.id), actor)
        tasks.handover(built, Ref.build(builder), actor)
        tasks.queued(looked, Ref.build(builder), actor)
        tasks.queued(kept, Ref.build(keeper), actor)
        rows = {row.name: row for row in counts.all_matching()}
        assert (rows["alpha"].plans_active, rows["alpha"].roles) == (1, {"scout": {"instances": 0, "queued": 0}, "builder": {"instances": 1, "queued": 1}}), "alpha: one plan active, the builder running with one task queued for it"
        assert (rows["beta"].plans_active, rows["beta"].roles) == (1, {"keeper": {"instances": 1, "queued": 1}})
        tasks.save(tasks.find(kept.id).completed(now, "kept"), actor)
        workers.save(workers.find(keeper.id).with_(adopted=True, state="released"), actor)
        assert {row.name: row.roles for row in counts.all_matching()}["beta"] == {"keeper": {"instances": 0, "queued": 0}}, "an instance that is released stops being counted, and so does its queue"
        assert {row.name: row.plans_active for row in counts.all_matching()}["beta"] == 0, "and beta's plan is no longer active once its task is done"
    status, shown = got(app, "/journal/organization", env)
    assert shown["folder"] == str(fixture.root) and shown["commit"] == commit, "the page answer names the actual folder and the commit it reads"
    alpha = next(domain for domain in shown["domains"] if domain["id"] == "alpha")
    beta = next(domain for domain in shown["domains"] if domain["id"] == "beta")
    builder_role = next(role for role in alpha["roles"] if role["id"] == "builder")
    assert status == 200 and shown["version"] and shown["problems"] == [] and "guidance" not in builder_role, "the answer holds the version, the problems and the Roles without their long guidance"
    status, builder_contract = got(app, "/journal/organization/roles/alpha/builder", env)
    assert status == 200 and builder_contract["guidance"] == "Guidance of builder.\n" and builder_contract["outputs"] == ["a report"], "a Role detail includes its AGENTS.md and whole contract"
    assert (alpha["plans_active"], builder_role["instances"], builder_role["queued"]) == (1, 1, 1) and alpha["plans"] == [{"id": plan.id, "title": "the floors", "phase": "planned", "phase_name": "Planned", "mode": "solo", "active": True, "tasks": [built.id, looked.id], "done": 0, "waits_on": "Role work"}], "with the counts and the board of plans"
    assert beta["plans"] == [{"id": plan.id, "title": "the floors", "phase": "done", "phase_name": "Done", "mode": "solo", "active": False, "tasks": [kept.id], "done": 1, "waits_on": ""}], "the same plan has a separate card in beta's phase with only beta's progress"
    listed = got(app, "/journal/domain_counts", env)[1]["rows"]
    assert {row["name"] for row in listed} == {"alpha", "beta"}, "the counts are rows of a table the viewer's sync carries"
    status, reloaded = answered(app, "POST", "/journal/organization/reload", b"{}", env)
    assert status == 200 and reloaded["version"] == shown["version"]
    with app.container.get(Scope).environment(1):
        domains = app.container.get(DomainRows)
        domains.task_tied(tasks.find(built.id), "beta", actor)
        assert {row.name: row.plans_active for row in counts.all_matching()} == {"alpha": 1, "beta": 1}, "alpha still holds the queued task"
        domains.task_tied(tasks.find(looked.id), "beta", actor)
        assert {row.name: row.plans_active for row in counts.all_matching()} == {"alpha": 0, "beta": 1}, "a task handed on to another domain's Role leaves the domain it came from at once"
        queued = {row.name: row.roles for row in counts.all_matching()}["alpha"]["builder"]["queued"]
        tasks.unqueued(Ref.build(builder), actor)
        assert queued == 1 and {row.name: row.roles for row in counts.all_matching()}["alpha"]["builder"]["queued"] == 0, "a queue emptied is counted again"
        assert {row.name: row.roles for row in counts.all_matching()}["alpha"]["builder"]["instances"] == 1, "the active builder instance is still counted before deletion"
        workers.delete(workers.find(builder.id), actor)
        assert {row.name: row.roles for row in counts.all_matching()}["alpha"]["builder"]["instances"] == 0, "deleting an active instance immediately changes its domain's figure"
