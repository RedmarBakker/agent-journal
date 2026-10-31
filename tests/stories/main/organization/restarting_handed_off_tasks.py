from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats
from tests.stories.fixtures.main.paused_organization_domain_handoff import PausedOrganizationDomainHandoff


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
