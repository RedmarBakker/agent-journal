from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats


@story(OrganizationPlanWithDomainSeats, subject=AgentRole.MAIN)
def test_a_blocked_plan_seat_reads_its_overview_and_can_stop(story):
    plan = story.plans.first
    story.agent_runs(story.agents.main, f"plan block {plan} 'waiting for the owner'").expect_command_passed()
    story.agent_starts_plan_seat(story.agents.main, plan).expect_allowed(story.agents.main)

    stopped = story.agent_stops_plan_seat(story.agents.main, plan)
    stopped.expect_refused_by_anything()
    stopped.expect_refusal_text(BriefingNudges.OVERVIEW_STOP.create().rendered())
    overview = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "environment overview")
    overview.expect_command_passed()
    story.agent_stops_plan_seat(story.agents.main, plan).expect_allowed(story.agents.main)

    story.expect_agent_is_the_plan_agent(story.agents.main, plan)
    story.expect_agent_session_in_environment(story.agents.main, f"plan-{plan}")
    story.expect_plan(plan, state=PlanState.BLOCKED)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
