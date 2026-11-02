from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.solo_plan_agent_task_started import SoloPlanAgentTaskStarted
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION


@story(SoloPlanAgentTaskStarted, subject=AgentRole.MAIN)
def test_blocking_a_plan_task_releases_its_plan_agent_and_unblock_leaves_it_free(story):
    plan, task = story.plans.first, story.tasks.first
    plan_agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
    blocked = story.user_blocks_task(task, "the owner needs time")
    blocked.expect_viewer_passed()
    story.expect_task(task, state=TaskState.BLOCKED)
    story.expect_task_unheld(task)
    story.expect_state_data(plan_agent, FollowingPlan, plan_id=plan, task_id=0)
    story.expect_stack(plan_agent, LeadingPlan, FollowingPlan)

    unblocked = story.user_did(f"/journal/tasks/{task}/unblock", {}, "user reopens the plan task")
    unblocked.expect_viewer_passed()
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_task_unheld(task)
    story.expect_state_data(plan_agent, FollowingPlan, plan_id=plan, task_id=0)
    story.expect_stack(plan_agent, LeadingPlan, FollowingPlan)
