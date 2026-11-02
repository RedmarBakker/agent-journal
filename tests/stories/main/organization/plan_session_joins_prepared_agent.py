from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_environment_prepared import OrganizationPlanEnvironmentPrepared


@story(OrganizationPlanEnvironmentPrepared, subject=AgentRole.MAIN)
def test_an_organization_plan_agent_joins_its_prepared_row_when_its_session_starts_during_launch(story):
    plan, task = story.plans.first, story.tasks.first
    configured = story.agent_runs(story.agents.subject, f"plan mode {plan} organization")
    configured.expect_command_passed()
    story.user_approves_plan(plan).expect_viewer_passed()

    started = story.agent_starts_an_organization_plan_with_its_session(story.agents.subject, plan)
    started.expect_command_passed()
    session_started = story.organization_plan_session_started()
    session_started.expect_allowed()
    plan_agent = story.organization_seat_agent_in_plan("plan", plan)

    story.expect_agent_session_in_environment(plan_agent, f"plan-{plan}")
    story.expect_row_count_in(f"plan-{plan}", "agents", 1)
    story.expect_state_data(plan_agent, LeadingPlan, plan_id=plan)
    story.expect_stack(plan_agent, LeadingPlan, FollowingPlan)
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)
