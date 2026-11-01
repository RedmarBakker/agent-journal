from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_handoff_seat import OrganizationPlanHandoffSeat


@story(OrganizationPlanHandoffSeat, subject=AgentRole.MAIN)
def test_pausing_an_organization_plan_preserves_its_plan_seat_stack(story):
    plan = story.plans.first
    paused = story.user_pauses_plan(plan)
    paused.expect_viewer_passed()
    story.settle()
    story.expect_plan(plan, state=PlanState.PAUSED)
    story.expect_openrig_seat_stopped("plan")
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
