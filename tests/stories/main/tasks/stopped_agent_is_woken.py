from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import OPEN_TASK_LIMIT_SECONDS
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.stopped_task import StoppedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(StoppedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_an_agent_stopped_with_work_in_hand_is_woken_after_the_set_minutes(story):
    story.agent_is_quiet_past(story.setting_seconds(TasksOptions.WAKE_MINUTES))
    story.expect_agent_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StoppedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_quiet_shorter_than_the_set_minutes_wakes_nobody(story):
    story.agent_is_quiet_for(minutes=story.setting(TasksOptions.WAKE_MINUTES) - 1)
    story.expect_agent_not_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(TasksOptions.WAKE_MINUTES, 0)
def test_a_wake_of_no_minutes_never_wakes(story):
    story.agent_stops()
    story.agent_is_quiet_past(OPEN_TASK_LIMIT_SECONDS)
    story.expect_agent_not_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(TasksOptions.WAKE_MINUTES, 10)
@setting(TasksOptions.WAKE_COUNT, 1)
def test_the_wake_stops_after_the_set_count(story):
    story.agent_stops()
    story.agent_is_quiet_past(story.setting_seconds(TasksOptions.WAKE_MINUTES))
    story.expect_agent_told(TasksNudges.STOPPED_WITH_WORK)
    story.agent_is_quiet_past(story.setting_seconds(TasksOptions.WAKE_MINUTES))
    story.expect_agent_not_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(TasksOptions.WAKE_MINUTES, 10)
def test_an_agent_with_nothing_in_hand_and_nothing_open_is_not_woken(story):
    story.agent_stops()
    story.agent_is_quiet_past(story.setting_seconds(TasksOptions.WAKE_MINUTES))
    story.expect_agent_not_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_stack(Ready)


@story(StartedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(TasksOptions.WAKE_MINUTES, 10)
def test_an_agent_following_a_plan_is_woken_with_the_plans_task(story):
    story.agent_stops()
    story.agent_is_quiet_past(story.setting_seconds(TasksOptions.WAKE_MINUTES))
    story.expect_agent_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_stack(Ready, FollowingPlan)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(TasksOptions.WAKE_MINUTES, 10)
def test_an_agent_waiting_on_a_run_is_not_woken(story):
    story.agent_runs("await 'the build' --until false")
    story.agent_stops()
    story.agent_is_quiet_past(story.setting_seconds(TasksOptions.WAKE_MINUTES))
    story.expect_agent_not_told(TasksNudges.STOPPED_WITH_WORK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working, ExternalWait)
