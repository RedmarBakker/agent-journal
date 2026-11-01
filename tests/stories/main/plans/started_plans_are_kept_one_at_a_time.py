from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.three_approved_plans import ThreeApprovedPlans


@story(ThreeApprovedPlans, subject=AgentRole.MAIN)
def test_a_main_agent_starts_one_plan_and_pauses_the_other(story):
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.agent_runs(story.agents.subject, f"task block {story.tasks.first} 'billing comes first'")
    story.user_starts_plan(story.plans.second)
    story.expect_plan(story.plans.first, state=PlanState.PAUSED)
    story.expect_plan(story.plans.second, state=PlanState.STARTED)
    story.expect_plan(story.plans.third, state=PlanState.APPROVED)
    story.expect_task(story.tasks.invoice, state=TaskState.STARTED)
    result = story.agent_writes(story.agents.subject, "invoice.py")
    result.expect_allowed()
    result.expect_agent_not_told(story.agents.subject, PlansNudges.PLAN_RETURN_QUESTION)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan, Working)
