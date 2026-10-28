from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.started_plan import StartedPlan
from tests.stories.fixtures.started_task import StartedTask


@story(StartedTask, end=[Ready, Working])
@setting(TasksOptions.FIRST_DELAY, 3)
def test_enough_edits_ask_for_a_log_once(story):
    story.repeat(int(story.setting(TasksOptions.FIRST_DELAY)) + 1, lambda: story.agent_writes("a.py"))
    story.expect_agent_told(TasksNudges.LOG_REQUEST)
    story.agent_writes("a.py")
    story.expect_agent_not_told(TasksNudges.LOG_REQUEST)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedTask, end=[Ready, Working])
@setting(TasksOptions.FIRST_DELAY, 3)
def test_reads_are_never_counted_as_edits(story):
    story.agent_reads(count=int(story.setting(TasksOptions.FIRST_DELAY)) + 1)
    story.expect_agent_not_told(TasksNudges.LOG_REQUEST)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedTask, end=[Ready, Working])
@setting(TasksOptions.TASK_REMINDER_INTERVAL, 2)
def test_every_set_number_of_edits_the_task_is_named_back(story):
    story.repeat(int(story.setting(TasksOptions.TASK_REMINDER_INTERVAL)) + 1, lambda: story.agent_writes("a.py"))
    story.expect_agent_told(TasksNudges.CURRENT_TASK_REMINDER)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedTask, end=[Ready, Working])
@setting(TasksOptions.LOG_LIMIT, 3)
def test_past_the_limit_the_next_write_waits_for_a_log_line(story):
    story.repeat(int(story.setting(TasksOptions.LOG_LIMIT)), lambda: story.agent_writes("a.py"))
    story.agent_writes("a.py")
    story.expect_refused(TasksNudges.LOG_EDIT_BLOCK)
    story.agent_reads()
    story.expect_allowed()
    story.agent_runs(f"task log {story.start.started_task} 'the footer has its links'")
    story.agent_writes("a.py")
    story.expect_allowed()


@story(StartedTask, end=[Ready, Working])
def test_a_quiet_quarter_hour_names_the_open_task(story):
    story.agent_is_quiet_for(minutes=16)
    story.expect_agent_told(TasksNudges.OPEN_TASK)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedTask, end=[Ready, Working])
def test_a_prompt_leaves_the_task_in_hand(story):
    story.agent_is_prompted("how far is the footer?")
    story.expect_stack(Ready, Working)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedPlan, end=[Ready, FollowingPlan])
@setting(TasksOptions.FIRST_DELAY, 3)
def test_a_plan_task_is_counted_the_same(story):
    story.repeat(int(story.setting(TasksOptions.FIRST_DELAY)) + 1, lambda: story.agent_writes("a.py"))
    story.expect_agent_told(TasksNudges.LOG_REQUEST)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
