from pathlib import Path

from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.rig_specs import RigSpecs
from journal.features.organization.support.seat_worker import SeatWorker
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.support.agent_token import AgentToken
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.organization_setup import OrganizationSetup
from tests.stories.main.plans.plan_agent_reads_its_plan import prepare_plan_agent_worktrees


WORKTREE_AGENT_SESSION = "dependent-domain-worktree-session"
TASK_BRIEF = "- Engineering uses the Security result and saves SECURITY.md"
SECURITY_BRIEF = "- Security records the policy decision"


@story(OrganizationSetup, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_a_dependent_organization_task_stays_with_its_domain_and_merges_on_its_plan_branch(story, monkeypatch):
    root = story.app.config.root
    prepare_plan_agent_worktrees(story, monkeypatch)
    story.configure_simulated_openrig()
    story.monkeypatch.setattr(WorkerRunner, "start", story.app.original_worker_start)

    environments = story.app.container.get(Environments)
    main = environments.existing("main")
    source = environments.made("smoke-3", Actor.system(), main.key, "worktree").name
    story.another_environment(source)
    WorkspaceWorktree.chosen(root, source).created()

    folder = Path(__file__).resolve().parents[3] / "stories" / "fixtures" / "main" / "organization_security_engineering"
    top, _, option = OrganizationOptions.FOLDER.key.partition(".")
    story.user_presses_in(source, "/journal/settings", {top: {option: str(folder)}}).expect_viewer_passed()
    story.user_presses_in(source, "/journal/organization/reload", {}).expect_viewer_passed()

    plan = story.user_creates_plan_in(source, "Security and Engineering plan")
    first = story.user_presses_in(source, f"/journal/plans/{plan}/tasks", {
        "title": "Security task", "brief": SECURITY_BRIEF, "domain": "security",
    })
    first.expect_viewer_passed()
    security = first.viewer_answer["id"]
    story.plans.first = plan
    story.tasks.first = security
    second = story.user_presses_in(source, f"/journal/plans/{plan}/tasks", {
        "title": "Engineering task", "brief": TASK_BRIEF, "domain": "engineering",
        "after": [security], "reason": "Engineering uses the Security result",
    })
    second.expect_viewer_passed()
    story.tasks.second = second.viewer_answer["id"]
    engineering = story.tasks.second

    story.session_starts_in(source, WORKTREE_AGENT_SESSION)
    coordinator = StoryAgent(AgentRole.MAIN, session=WORKTREE_AGENT_SESSION)
    result = story.agent_in_runs(story.agents.main, source, WORKTREE_AGENT_SESSION, f"plan mode {plan} organization")
    result.expect_command_passed()
    story.user_presses_in(source, f"/journal/plans/{plan}/approve", {}).expect_viewer_passed()

    plan_row = story.app.container.get(Plans).global_matching(id=plan)[0]
    with story.app.container.get(Scope).environment(plan_row.environment_id):
        contracts = story.app.container.get(Organization).reload()
        provider = story.app.container.get(Providers).lookup(story.provider)
        domains = tuple(domain.id for domain in contracts.domains)
        story.app.container.get(RigSpecs).write(
            story.plan_rig_name(plan), contracts, domains, root,
            lambda seat: SeatWorker(Actor.agent(""), AgentToken(f"story-seat-{plan}-{seat.qualified}"), "main", seat.qualified, story.plan_rig_name(plan)),
            provider,
        )

    result = story.agent_in_runs(story.agents.main, source, WORKTREE_AGENT_SESSION, f"plan start {plan}")
    result.expect_command_passed()
    result.expect_command_text(f"plan {plan} started")
    plan_seat = story.organization_seat_agent_in_plan("plan", plan)
    started = story.agent_starts_organization_seat_in_plan(plan_seat, "plan", plan)
    started.expect_agent_told(plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                              task=security, domain="security")
    story.agent_runs_from_plan_organization_seat(plan_seat, "plan", "environment overview").expect_command_passed()
    story.agent_runs_from_plan_organization_seat(
        plan_seat, "plan", f"organization handoff {security} domain:security",
    ).expect_command_passed()

    security_domain = story.organization_seat_agent_in_plan("domain:security", plan)
    story.agent_starts_organization_seat_in_plan(security_domain, "domain:security", plan).expect_allowed(security_domain)
    story.agent_runs_from_openrig_organization_seat(security_domain, "domain:security", "organization inbox").expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        security_domain, "domain:security", f"organization handoff {security} role:security/reviewer",
    ).expect_command_passed()
    shared_rig = story.app.container.get(RigStaffing).shared_rig_name(plan_row.environment_id)
    reviewer = story.organization_seat_agent("role:security/reviewer", shared_rig)
    story.agent_starts_organization_seat(reviewer, "role:security/reviewer", shared_rig).expect_allowed(reviewer)
    story.agent_runs_from_openrig_organization_seat(
        reviewer, "role:security/reviewer", "organization inbox", shared_rig,
    ).expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        reviewer, "role:security/reviewer", f"organization handoff {security} domain:security", shared_rig,
    ).expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(security_domain, "domain:security", "organization inbox").expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        security_domain, "domain:security", f"organization handoff {security} plan",
    ).expect_command_passed()
    story.agent_starts_organization_seat_in_plan(plan_seat, "plan", plan).expect_allowed(plan_seat)
    story.agent_runs_from_plan_organization_seat(plan_seat, "plan", "environment overview").expect_command_passed()
    story.expect_stack(plan_seat, LeadingPlan, FollowingPlan)

    completed = story.agent_runs_from_plan_organization_seat(
        plan_seat, "plan", f"task complete {security} --how 'Security recorded the policy decision'",
    )
    completed.expect_command_passed()
    story.settle()
    story.expect_task_in(source, security, TaskState.COMPLETED.value)
    story.expect_task_in(source, engineering, TaskState.OPEN.value)
    running_plan = story.user_opens_in(source, f"/journal/plans?ids={plan}")
    running_plan.expect_viewer_passed()
    running_plan.expect_viewer_rows("rows", "state", [PlanState.STARTED.value])
    story.expect_stack(plan_seat, LeadingPlan, FollowingPlan)
    ready = story.agent_starts_organization_seat_in_plan(plan_seat, "plan", plan)
    ready.expect_agent_told(plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                            task=engineering, domain="engineering")
    story.agent_runs_from_plan_organization_seat(plan_seat, "plan", "environment overview").expect_command_passed()
    status, answer = story.session_posted_hook(
        WORKTREE_AGENT_SESSION, {"X-Journal-Env": source}, "Stop", {},
    )
    stopped = story.hook_observed("the coordinator stops in the plan environment", status, answer, source)
    stopped.expect_allowed(coordinator)
    story.settle()
    story.expect_task_in(source, engineering, TaskState.OPEN.value)
    story.expect_environment_absent(f"task-{engineering}")

    waiting = story.agent_stops_plan_seat(plan_seat, plan)
    waiting.expect_allowed(plan_seat)
    waiting.expect_agent_not_told(plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                  task=engineering, domain="engineering")
    story.agent_runs_from_plan_organization_seat(
        plan_seat, "plan", f"organization handoff {engineering} domain:engineering",
    ).expect_command_passed()
    engineering_domain = story.organization_seat_agent_in_plan("domain:engineering", plan)
    story.agent_starts_organization_seat_in_plan(
        engineering_domain, "domain:engineering", plan,
    ).expect_allowed(engineering_domain)
    inbox = story.agent_runs_from_openrig_organization_seat(engineering_domain, "domain:engineering", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(TASK_BRIEF)
    previous = story.agent_runs_from_openrig_organization_seat(
        engineering_domain, "domain:engineering", f"task show {security}",
    )
    previous.expect_command_passed()
    previous.expect_command_text("outcome: Security recorded the policy decision")

    story.agent_runs_from_openrig_organization_seat(
        engineering_domain, "domain:engineering", f"organization handoff {engineering} role:engineering/builder",
    ).expect_command_passed()
    worker = StoryAgent(AgentRole.WORKER, number=story.newest_in("workers", source))
    story.expect_worker_role_job(worker, engineering, TASK_BRIEF, SECURITY_BRIEF)
    story.expect_no_user_message_text_in(source, TASK_BRIEF)
    story.agent_starts_role_session(worker).expect_allowed(worker)
    story.agent_clocks_in(worker).expect_command_passed()
    task_details = story.agent_runs_from_openrig_organization_seat(worker, "role:engineering/builder", f"task show {engineering}")
    task_details.expect_command_passed()
    task_details.expect_command_text("task Engineering task")
    task_details.expect_command_text("Engineering uses the Security result")
    prior_details = story.agent_runs_from_openrig_organization_seat(worker, "role:engineering/builder", f"task show {security}")
    prior_details.expect_command_passed()
    prior_details.expect_command_text("outcome: Security recorded the policy decision")
    story.agent_writes_from_organization_role_seat(worker, "role:engineering/builder", "SECURITY.md").expect_allowed(worker)
    story.expect_agent_session_in_environment(worker, source)

    source_tree = WorkspaceWorktree.chosen(root, source).path
    (source_tree / "SECURITY.md").write_text("Engineering used the Security result\n")
    story.git_in(source_tree, "add", "SECURITY.md")
    story.git_in(source_tree, "-c", "user.email=story@example.com", "-c", "user.name=Story",
                 "commit", "-q", "-m", "save the Engineering result")
    story.expect_commit_in(source_tree, "save the Engineering result")
    story.expect_project_file_is(f".claude/worktrees/{source}/SECURITY.md", "Engineering used the Security result\n")
    story.expect_no_project_file("SECURITY.md")
    story.expect_task_in(source, engineering, TaskState.STARTED.value)
    story.agent_proves(worker, 1, "SECURITY.md: Engineering used the Security result")
    story.agent_clocks_out(worker, "the Engineering result is ready for Domain check")

    story.agent_runs_from_openrig_organization_seat(engineering_domain, "domain:engineering", f"worker check {worker} 1").expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        engineering_domain, "domain:engineering", f"organization handoff {engineering} plan",
    ).expect_command_passed()
    story.expect_task_in(source, engineering, TaskState.STARTED.value)
    merged = story.agent_runs_from_plan_organization_seat(plan_seat, "plan", f"worker merge {worker}")
    merged.expect_command_passed()
    merged.expect_command_text(f"task {engineering} done")
    story.settle()

    story.expect_task_in(source, security, TaskState.COMPLETED.value)
    story.expect_task_in(source, engineering, TaskState.COMPLETED.value)
    story.expect_no_user_message_text_in(source, TASK_BRIEF)
    story.expect_project_file_is(f".claude/worktrees/{source}/SECURITY.md", "Engineering used the Security result\n")
    plan_status = story.user_opens_in(source, f"/journal/plans?ids={plan}")
    plan_status.expect_viewer_passed()
    plan_status.expect_viewer_rows("rows", "state", [PlanState.FINISHED.value])
    story.expect_stack(plan_seat, LeadingPlan, FollowingPlan)
