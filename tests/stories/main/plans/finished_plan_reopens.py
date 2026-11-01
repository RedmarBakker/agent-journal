from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.finished_plan import FinishedPlan


@story(FinishedPlan, subject=AgentRole.MAIN)
def test_a_task_added_to_a_finished_plan_reopens_it_and_plan_start_takes_it_up(story):
    added = story.user_adds_plan_task(story.plans.first, "the footer links")
    story.last_step.expect_agent_told(story.agents.subject, PlansNudges.PLAN_REOPENED, n=story.plans.first)
    story.last_step.expect_agent_not_told(story.agents.subject, PlansNudges.PLAN_STALLED)
    story.expect_task(added, state=TaskState.OPEN)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(added, state=TaskState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.COMPLETED)
    story.expect_task(story.tasks.second, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
