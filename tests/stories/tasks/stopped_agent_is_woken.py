from tests.stories.fixtures.stopped_with_work import StoppedWithWork
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.started_plan import StartedPlan
from tests.stories.fixtures.started_task import StartedTask
from tests.stories.fixtures.working_agent import WorkingAgent


@story(StoppedWithWork, end=[Ready, Working])
def test_an_agent_stopped_with_work_in_hand_is_woken_after_the_set_minutes(story):
    story.agent_is_quiet_for(minutes=story.setting(TasksOptions.WAKE_MINUTES) + 1)
    story.expect_agent_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StoppedWithWork, end=[Ready, Working])
def test_a_quiet_shorter_than_the_set_minutes_wakes_nobody(story):
    story.agent_is_quiet_for(minutes=story.setting(TasksOptions.WAKE_MINUTES) - 1)
    story.expect_agent_not_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedTask, end=[Ready, Working])
@setting(TasksOptions.WAKE_MINUTES, 0)
def test_a_wake_of_no_minutes_never_wakes(story):
    story.agent_stops()
    story.agent_is_quiet_for(minutes=20)
    story.expect_agent_not_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedTask, end=[Ready, Working])
@setting(TasksOptions.WAKE_MINUTES, 10)
@setting(TasksOptions.WAKE_COUNT, 1)
def test_the_wake_stops_after_the_set_count(story):
    story.agent_stops()
    story.agent_is_quiet_for(minutes=story.setting(TasksOptions.WAKE_MINUTES) + 1)
    story.expect_agent_told(TasksNudges.STOPPED_WITH_WORK)
    story.agent_is_quiet_for(minutes=story.setting(TasksOptions.WAKE_MINUTES) + 1)
    story.expect_agent_not_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(WorkingAgent, end=[Ready])
@setting(TasksOptions.WAKE_MINUTES, 10)
def test_an_agent_with_nothing_in_hand_and_nothing_open_is_not_woken(story):
    story.agent_stops()
    story.agent_is_quiet_for(minutes=story.setting(TasksOptions.WAKE_MINUTES) + 1)
    story.expect_agent_not_told(TasksNudges.STOPPED_WITH_WORK)


@story(StartedPlan, end=[Ready, FollowingPlan])
@setting(TasksOptions.WAKE_MINUTES, 10)
def test_an_agent_following_a_plan_is_woken_with_the_plans_task(story):
    story.agent_stops()
    story.agent_is_quiet_for(minutes=story.setting(TasksOptions.WAKE_MINUTES) + 1)
    story.expect_agent_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)


@story(StartedTask, end=[Ready, Working, ExternalWait])
@setting(TasksOptions.WAKE_MINUTES, 10)
def test_an_agent_waiting_on_a_run_is_not_woken(story):
    story.agent_runs("await 'the build' --until false")
    story.agent_stops()
    story.agent_is_quiet_for(minutes=story.setting(TasksOptions.WAKE_MINUTES) + 1)
    story.expect_agent_not_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
