from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.finished_plan import FinishedPlan


@story(FinishedPlan, mode=BUILDER_MODE)
def test_a_task_added_to_a_finished_plan_reopens_it_and_plan_start_takes_it_up(story):
    added = story.user_adds_plan_task(story.start.plan, "the footer links")
    story.expect_agent_told(PlansNudges.PLAN_REOPENED, n=story.start.plan)
    story.expect_agent_not_told(PlansNudges.PLAN_STALLED)
    story.expect_task(added, state=TaskState.OPEN)
    story.agent_runs(f"plan start {story.start.plan}")
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_task(added, state=TaskState.STARTED)
    story.expect_task(story.start.first_task, state=TaskState.COMPLETED)
    story.expect_task(story.start.second_task, state=TaskState.COMPLETED)
    story.expect_stack(Ready, FollowingPlan)
