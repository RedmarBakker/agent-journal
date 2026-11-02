from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_agent_plan_started import PlanAgentPlanStarted
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION
from tests.stories.fixtures.main.solo_plan_agent_task_started import SoloPlanAgentTaskStarted


def plan_agent() -> StoryAgent:
    return StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)


@story(PlanAgentPlanStarted, subject=AgentRole.MAIN)
def test_a_plan_agents_floor_keeps_its_plan_after_its_session_starts(story):
    agent = plan_agent()
    environment = f"plan-{story.plans.first}"
    story.session_starts_in(environment, PLAN_AGENT_SESSION).expect_allowed()
    result = story.agent_in_runs(agent, environment, PLAN_AGENT_SESSION, "environment overview")
    result.expect_command_passed()
    result = story.agent_in_runs(agent, environment, PLAN_AGENT_SESSION, f"plan show {story.plans.first}")
    result.expect_command_passed()
    story.expect_state_data(agent, LeadingPlan, plan_id=story.plans.first)
    story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)


@story(SoloPlanAgentTaskStarted, subject=AgentRole.MAIN)
def test_a_plan_agents_floor_keeps_its_plan_after_it_takes_its_first_task(story):
    agent = plan_agent()
    plan, task = story.plans.first, story.tasks.first
    result = story.agent_in_runs(agent, f"plan-{plan}", PLAN_AGENT_SESSION, f"task show {task}")
    result.expect_command_passed()
    story.expect_state_data(agent, LeadingPlan, plan_id=plan)
    story.expect_state_data(agent, FollowingPlan, plan_id=plan, task_id=task)
    story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)


@story(SoloPlanAgentTaskStarted, subject=AgentRole.MAIN)
def test_a_restarted_plan_agents_floor_keeps_its_plan(story):
    agent = plan_agent()
    plan, task = story.plans.first, story.tasks.first
    story.user_pauses_plan(plan).expect_viewer_passed()
    story.user_did(f"/journal/tasks/{task}/unblock", {}, "user unblocks the plan task").expect_viewer_passed()
    story.user_starts_plan(plan).expect_viewer_passed()
    story.session_starts_in(f"plan-{plan}", PLAN_AGENT_SESSION, "resume").expect_allowed()
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_state_data(agent, LeadingPlan, plan_id=plan)
    story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)
