from journal.engine.states.void import Void
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_without_domain_seats import (
    OrganizationPlanWithoutDomainSeats,
    TASK_BRIEF,
)
from tests.stories.fixtures.main.organization_role_worker_clocked_in import (
    OrganizationRoleWorkerClockedIn,
    STALE_BRIEF,
)


@story(OrganizationRoleWorkerClockedIn, subject=AgentRole.MAIN)
def test_a_first_plan_handoff_places_and_wakes_its_domain_before_the_domain_sends_work_to_a_role(story):
    plan, task = story.plans.first, story.tasks.first
    worker = story.agents.workers.first()
    story.expect_worker_role_job(worker, task, TASK_BRIEF, STALE_BRIEF)
    story.expect_no_prerequisite_results_in_role_job(worker, TASK_BRIEF)
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
    story.expect_organization_seat_routing_guidance(story.plan_rig_name(plan))
    story.expect_stack(worker, Void)


@story(OrganizationPlanWithoutDomainSeats, subject=AgentRole.MAIN)
def test_a_plan_refuses_to_handoff_to_a_domain_outside_its_contract(story):
    inbox = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text("no tasks handed to plan")
    result = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {story.tasks.first} domain:gamma",
    )
    result.expect_command_refused()
    story.expect_task(story.tasks.first, state=TaskState.OPEN, delegated=False)
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan)


@story(OrganizationPlanWithoutDomainSeats, subject=AgentRole.MAIN)
def test_a_plan_refuses_to_expand_a_domain_on_openrig_that_drops_member_environment(story):
    story.simulated_seats().version = "0.7.5"
    story.simulated_seats().cli_version = "0.7.6"
    task = story.tasks.first
    result = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    result.expect_command_refused()
    result.expect_command_text("OpenRig daemon 0.7.5 cannot place seats; it needs 0.7.6 or later: restart the daemon")
    story.expect_task(task, state=TaskState.OPEN, delegated=False)
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan)
