from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_seat import OrganizationPlanSeat


@story(OrganizationPlanSeat, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_handoff_wakes_an_idle_domain_seat_to_read_its_inbox(story):
    plan = story.plans.first
    task = story.tasks.first
    started = story.agent_runs(story.agents.main, f"plan start {plan}")
    started.expect_command_passed()
    domain = story.organization_seat_agent("domain:alpha")
    domain_started = story.agent_starts_organization_seat(domain, "domain:alpha")
    domain_started.expect_agent_not_told(domain, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha")
    story.organization_seat_goes_idle(domain, "domain:alpha")

    handed = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    handed.expect_command_passed()
    handed.expect_command_text(f"task {task} routed from plan to domain:alpha")
    story.expect_openrig_seat_received(domain, f"plan-{plan}", "domain:alpha", "journal organization inbox")
    story.expect_task_tied_to_domain(task, "alpha")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_stack(story.agents.main, CoordinatingPlans, OrchestratingPlan)


@story(OrganizationPlanSeat, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_domain_seat_with_an_unread_handoff_is_told_at_start_and_stop(story):
    plan = story.plans.first
    task = story.tasks.first
    story.agent_runs(story.agents.main, f"plan start {plan}").expect_command_passed()
    handoff = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    handoff.expect_command_passed()

    domain = story.organization_seat_agent("domain:alpha")
    started = story.agent_starts_organization_seat(domain, "domain:alpha")
    started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)

    stopped = story.agent_stops_organization_seat(domain, "domain:alpha")
    stopped.expect_refused(domain, OrganizationNudges.UNREAD_HANDOFF)

    inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")
    stopped = story.agent_stops_organization_seat(domain, "domain:alpha")
    stopped.expect_allowed()

    story.expect_stack(story.agents.main, CoordinatingPlans, OrchestratingPlan)
