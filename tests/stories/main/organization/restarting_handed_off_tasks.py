from journal.engine.states.void import Void
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats
from tests.stories.fixtures.main.paused_organization_domain_handoff import PausedOrganizationDomainHandoff
from tests.stories.fixtures.main.paused_organization_plan_role_route import PausedOrganizationPlanRoleRoute


@story(PausedOrganizationDomainHandoff, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_restarting_a_plan_marks_its_read_domain_handoff_unread(story):
    plan, task = story.plans.first, story.tasks.first
    story.user_starts_plan(plan).expect_viewer_passed()

    domain = story.organization_seat_agent("domain:alpha")
    domain_started = story.agent_starts_organization_seat(domain, "domain:alpha")
    domain_started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
    inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")

    plan_seat = story.organization_seat_agent("plan")
    plan_started = story.agent_starts_plan_seat(plan_seat, plan)
    plan_started.expect_agent_not_told(
        plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha",
    )
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.OPEN, delegated=False)
    story.expect_stack(plan_seat, LeadingPlan, FollowingPlan)


@story(OrganizationPlanWithDomainSeats, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_running_plan_does_not_repeat_a_read_domain_handoff(story):
    plan, task = story.plans.first, story.tasks.first

    plan_seat = story.organization_seat_agent("plan")
    started = story.agent_starts_plan_seat(plan_seat, plan)
    started.expect_agent_told(
        plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha",
    )
    handoff = story.agent_runs_as_organization_seat(
        plan_seat, "plan", f"organization handoff {task} domain:alpha",
    )
    handoff.expect_command_passed()
    domain = story.organization_seat_agent("domain:alpha")
    domain_started = story.agent_starts_organization_seat(domain, "domain:alpha")
    domain_started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
    inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()

    resumed_domain = story.agent_resumes_the_session(domain)
    resumed_domain.expect_agent_not_told(domain, OrganizationNudges.UNREAD_HANDOFF)
    resumed_plan = story.agent_resumes_the_session(plan_seat)
    resumed_plan.expect_agent_not_told(
        plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha",
    )
    stopped_plan = story.agent_stops_plan_seat(plan_seat, plan)
    stopped_plan.expect_agent_not_told(
        plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha",
    )
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_stack(domain, LeadingPlan, FollowingPlan)


@story(PausedOrganizationPlanRoleRoute, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_restarting_a_plan_sends_an_ended_role_task_to_a_fresh_role_job(story):
    story.monkeypatch.setattr(WorkerRunner, "start", story.app.original_worker_start)
    story.plays_in(BUILDER_MODE)
    plan, task = story.plans.first, story.tasks.first
    story.user_rewrites_the_brief(task, "- the earlier task brief").expect_viewer_passed()
    story.user_rewrites_the_brief(task, "- the restarted Role gets this task").expect_viewer_passed()

    domain = story.organization_seat_agent("domain:alpha")
    handed_to_role = story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    handed_to_role.expect_command_passed()
    story.fixture.workers.first = story.newest("workers")
    ended_worker = story.agents.workers.first()
    story.expect_worker_role_job(ended_worker, task, "- the restarted Role gets this task", "- the earlier task brief")
    story.agent_starts_role_session(ended_worker).expect_allowed(ended_worker)
    story.expect_role_job_prompt(ended_worker, "- the restarted Role gets this task", "- the earlier task brief", "journal clock-in")
    story.agent_clocks_in(ended_worker).expect_command_passed()
    story.worker_run_ends_without_clocking_out(ended_worker)
    story.expect_task(task, state=TaskState.STARTED, delegated=True)
    story.expect_worker(ended_worker, state=WorkerState.UNFINISHED)

    story.user_starts_plan(plan).expect_viewer_passed()
    story.expect_plan(plan, state=PlanState.STARTED)

    domain = story.organization_seat_agent("domain:alpha")
    domain_started = story.agent_starts_organization_seat(domain, "domain:alpha")
    domain_started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
    inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")
    inbox.expect_command_text(f"worker {ended_worker} holds this task")

    handed_to_role = story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    handed_to_role.expect_command_passed()
    handed_to_role.expect_command_text(f"task {task} routed from domain:alpha to role:alpha/builder")
    handed_to_role.expect_command_text(f"worker {ended_worker} Builder task {task} told")

    story.fixture.workers.first = story.newest("workers")
    worker = story.agents.workers.first()
    story.expect_worker(worker, state=WorkerState.DISPATCHED)
    story.expect_worker_role_job(worker, task, "- the restarted Role gets this task", "- the earlier task brief")
    role_started = story.agent_starts_role_session(worker)
    role_started.expect_allowed(worker)
    story.expect_openrig_seat_environment(worker, "role:alpha/builder")
    story.expect_role_job_prompt(worker, "- the restarted Role gets this task", "- the earlier task brief", "journal clock-in")
    story.agent_clocks_in(worker).expect_command_passed()
    story.expect_task(task, state=TaskState.STARTED, delegated=True)
    story.expect_worker(worker, state=WorkerState.READY)

    plan_seat = story.organization_seat_agent("plan")
    restarted_plan = story.agent_starts_plan_seat(plan_seat, plan)
    restarted_plan.expect_agent_not_told(
        plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha",
    )
    story.expect_stack(worker, Void, WorkingTask)
