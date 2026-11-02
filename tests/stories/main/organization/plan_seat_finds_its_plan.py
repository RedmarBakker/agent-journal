from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.plans.support.plan_agents import PlanAgents
from journal.repositories.plans import Plans
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_seat_without_binding import OrganizationPlanSeatWithoutBinding


@story(OrganizationPlanSeatWithoutBinding, subject=AgentRole.MAIN)
def test_a_plan_seats_first_command_finds_the_plan_stored_in_its_owners_environment(story):
    plan = story.plans.first
    plan_seat = story.organization_seat_agent_in_plan("plan", plan)
    overview = story.agent_runs_from_plan_organization_seat(plan_seat, "plan", "environment overview")
    overview.expect_command_passed()
    overview.expect_command_text(f"plan {plan} started: p")
    overview.expect_command_text("first")
    overview.expect_command_text("domain:alpha")

    plan_row = story.app.container.get(Plans).global_matching(id=plan)[0]
    plan_agent = story.app.container.get(PlanAgents).agent(plan_row)
    story.expect_row_in(f"plan-{plan}", "agents", plan_agent.row_id, {"is_overview_read": True})
    story.agent_starts_plan_seat(story.agents.main, plan).expect_allowed(story.agents.main)
    story.expect_agent_is_the_plan_agent(story.agents.main, plan)
    story.expect_stack(story.agents.main, LeadingPlan)
