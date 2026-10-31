from journal.engine.states.void import Void
from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_without_domain_seats import (
    OrganizationPlanWithoutDomainSeats,
    TASK_BRIEF,
)

STALE_BRIEF = "the earlier task brief"


@story(OrganizationPlanWithoutDomainSeats, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_first_plan_handoff_places_and_wakes_its_domain_before_the_domain_sends_work_to_a_role(story):
    plan, task = story.plans.first, story.tasks.first
    handed_to_domain = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    handed_to_domain.expect_command_passed()
    handed_to_domain.expect_command_text(f"task {task} routed from plan to domain:alpha")

    domain = story.organization_seat_agent("domain:alpha")
    story.expect_openrig_seat_environment(domain, "domain:alpha")
    story.expect_openrig_seat_received(domain, f"plan-{plan}", "domain:alpha", OrganizationSeatRouting.handoff_prompt)
    started = story.agent_starts_organization_seat(domain, "domain:alpha")
    started.expect_allowed(domain)
    inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")
    inbox.expect_command_text(TASK_BRIEF)

    handed_to_role = story.agent_runs_from_openrig_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    handed_to_role.expect_command_passed()
    worker_number = story.newest("workers")
    story.fixture.workers.first = worker_number
    worker = story.agents.workers.first()
    story.expect_worker_role_job(worker, task, TASK_BRIEF, STALE_BRIEF)
    role_started = story.agent_starts_role_session(worker)
    role_started.expect_allowed(worker)
    story.expect_openrig_seat_environment(worker, "role:alpha/builder")
    story.expect_role_job_prompt(worker, TASK_BRIEF, STALE_BRIEF, "journal clock-in")

    role_inbox = story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "organization inbox")
    role_inbox.expect_command_passed()
    role_inbox.expect_command_text(TASK_BRIEF)
    clocked_in = story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in")
    clocked_in.expect_command_passed()
    story.expect_stack(worker, Void, WorkingTask)
    proven = story.agent_runs_from_openrig_organization_seat(
        worker, "role:alpha/builder", f"proof 1 'the current task brief is met: {TASK_BRIEF.removeprefix('- ')}'",
    )
    proven.expect_command_passed()
    clocked_out = story.agent_runs_from_openrig_organization_seat(
        worker, "role:alpha/builder", "clock-out 'the task brief is met'",
    )
    clocked_out.expect_command_passed()

    checked = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"worker check {worker} 1",
    )
    checked.expect_command_passed()
    returned = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} plan",
    )
    returned.expect_command_passed()
    plan_inbox = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "organization inbox")
    plan_inbox.expect_command_passed()
    plan_inbox.expect_command_text(f"plan {plan} task {task}: first")
    merged = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"worker merge {worker}")
    merged.expect_command_passed()

    story.expect_task(task, state=TaskState.COMPLETED)
    story.expect_worker(worker, state=WorkerState.MERGED)
    story.expect_plan(plan, state=PlanState.FINISHED)
    story.expect_organization_seat_routing_guidance(f"plan-{plan}")
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan)


@story(OrganizationPlanWithoutDomainSeats, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_refuses_to_handoff_to_a_domain_outside_its_contract(story):
    result = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {story.tasks.first} domain:gamma",
    )
    result.expect_command_refused()
    story.expect_task(story.tasks.first, state=TaskState.OPEN, delegated=False)
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan)


@story(OrganizationPlanWithoutDomainSeats, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_refuses_to_expand_a_domain_on_openrig_that_drops_member_environment(story):
    story.simulated_seats().version = "0.7.5"
    task = story.tasks.first
    result = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    result.expect_command_refused()
    result.expect_command_text("OpenRig 0.7.5; dynamic organization seat placement requires OpenRig 0.7.6 or later")
    story.expect_task(task, state=TaskState.OPEN, delegated=False)
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan)
