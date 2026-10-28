from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.outside_task_over_plan import OutsideTaskOverPlan
from tests.stories.fixtures.plan_paused_by_user import PlanPausedByUser


@story(OutsideTaskOverPlan, end=[Ready])
def test_the_user_pausing_the_plan_meanwhile_leaves_the_outside_task_in_hand(story):
    story.user_pauses_plan(story.start.plan)
    story.expect_plan(story.start.plan, state=PlanState.PAUSED)
    story.agent_stops()
    story.expect_refused(TasksNudges.TASK_CONTINUATION)
    story.agent_runs(f"task complete {story.start.outside_task} --how done")
    story.expect_plan(story.start.plan, state=PlanState.PAUSED)


@story(OutsideTaskOverPlan, end=[Ready, FollowingPlan])
def test_the_plan_carries_on_after_the_outside_task_completes(story):
    story.agent_runs(f"task complete {story.start.outside_task} --how done")
    story.expect_task(story.start.outside_task, state=TaskState.COMPLETED)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)


@story(PlanPausedByUser, end=[Ready])
def test_a_plan_the_user_paused_stays_quiet_at_the_stop(story):
    story.agent_stops()
    story.expect_allowed()
    story.expect_task(story.start.first_task, state=TaskState.PAUSED)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)
    story.expect_plan(story.start.plan, state=PlanState.PAUSED)
