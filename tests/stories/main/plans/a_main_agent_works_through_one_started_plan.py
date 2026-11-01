from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_plan import StartedPlan


@story(StartedPlan, subject=AgentRole.MAIN)
def test_a_main_agent_with_a_plan_task_in_hand_is_refused_a_second_plan(story):
    second_plan = story.user_creates_plan("q", "b")
    third_task = story.user_adds_plan_task(second_plan, "third")
    story.user_approves_plan(second_plan)
    result = story.agent_runs(story.agents.subject, f"plan start {second_plan}")
    result.expect_command_refused()
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_plan(second_plan, state=PlanState.APPROVED)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_task(third_task, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
