from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_with_stale_agent_link import OrganizationPlanWithStaleAgentLink
from tests.stories.fixtures.main.organization_plan_with_legacy_agent_links import OrganizationPlanWithLegacyAgentLinks


@story(OrganizationPlanWithStaleAgentLink, subject=AgentRole.MAIN)
def test_a_fresh_plan_seats_overview_uses_its_own_row_instead_of_an_older_owner_link(story):
    plan = story.plans.first
    seat = story.organization_seat_agent_in_plan("plan", plan)
    result = story.agent_runs_from_plan_organization_seat(seat, "plan", "environment overview")
    result.expect_command_passed()
    result.expect_command_text(f"plan {plan} started: p")
    story.expect_plan_agent_in_its_environment(plan, is_overview_read=True)
    story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)


@story(OrganizationPlanWithLegacyAgentLinks, subject=AgentRole.MAIN)
def test_a_plan_seat_with_legacy_links_reads_the_latest_plan_row_before_its_overview(story):
    plan = story.plans.first
    seat = story.organization_seat_agent_in_plan("plan", plan)
    story.agent_runs_from_plan_organization_seat(seat, "plan", f"plan show {plan}").expect_command_passed()
    story.agent_starts_organization_seat_in_plan(seat, "plan", plan).expect_allowed(seat)
    story.agent_runs_from_plan_organization_seat(seat, "plan", "environment overview").expect_command_passed()
    story.expect_agent_is_the_plan_agent(seat, plan)
    story.expect_plan_agent_in_its_environment(plan, link_count=2, is_overview_read=True)
    story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)
