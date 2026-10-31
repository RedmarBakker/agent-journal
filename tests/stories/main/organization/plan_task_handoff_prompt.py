from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_handoff_seat import DelegatedOrganizationPlanHandoffSeat, OrganizationPlanHandoffSeat


@story(OrganizationPlanHandoffSeat, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_fresh_plan_seat_is_told_to_handoff_its_domain_task(story):
    plan = story.plans.first
    task = story.tasks.first
    handoff = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"organization handoff {task} domain:alpha")
    handoff.expect_command_passed()
    handoff.expect_command_text(f"task {task} routed from plan to domain:alpha")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


@story(OrganizationPlanHandoffSeat, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_seat_cannot_stop_before_handing_off_its_domain_task(story):
    plan = story.plans.first
    task = story.tasks.first
    stopped = story.agent_stops_plan_seat(story.agents.main, plan)
    stopped.expect_refused_by_anything()
    stopped.expect_refusal_text(f"plan task {task} waits for handoff to domain:alpha; run `journal organization handoff {task} domain:alpha`")
    handoff = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"organization handoff {task} domain:alpha")
    handoff.expect_command_passed()
    story.agent_stops_plan_seat(story.agents.main, plan).expect_allowed()
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


@story(DelegatedOrganizationPlanHandoffSeat, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_delegated_plan_task_still_waits_for_domain_handoff(story):
    handoff = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"organization handoff {story.tasks.first} domain:alpha")
    handoff.expect_command_passed()
    handoff.expect_command_text(f"task {story.tasks.first} routed from plan to domain:alpha")
    story.expect_task(story.tasks.first, state=TaskState.OPEN, delegated=True)
    story.agent_starts_a_session(story.agents.workers.first())
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


