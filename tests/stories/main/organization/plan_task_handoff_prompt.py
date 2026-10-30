from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, WorkersOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.organization_plan_seat import OrganizationPlanSeat


@story(OrganizationPlanSeat, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.MODE, ORCHESTRATOR_MODE)
def test_a_fresh_plan_seat_is_told_to_handoff_its_domain_task(story):
    plan = story.plans.first
    task = story.tasks.first
    started = story.agent_runs(story.agents.main, f"plan start {plan}")
    started.expect_command_passed()
    seat = story.agent_starts_plan_seat(story.agents.main, plan)
    seat.expect_agent_told(story.agents.main, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha")
    handoff = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"organization handoff {task} domain:alpha")
    handoff.expect_command_passed()
    handoff.expect_command_text(f"task {task} routed from plan to domain:alpha")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


@story(OrganizationPlanSeat, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.MODE, ORCHESTRATOR_MODE)
def test_a_plan_seat_cannot_stop_before_handing_off_its_domain_task(story):
    plan = story.plans.first
    task = story.tasks.first
    story.agent_runs(story.agents.main, f"plan start {plan}").expect_command_passed()
    story.agent_starts_plan_seat(story.agents.main, plan)
    stopped = story.agent_stops_plan_seat(story.agents.main, plan)
    stopped.expect_refused_by_anything()
    stopped.expect_refusal_text(f"plan task {task} waits for handoff to domain:alpha; run `journal organization handoff {task} domain:alpha`")
    handoff = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"organization handoff {task} domain:alpha")
    handoff.expect_command_passed()
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


