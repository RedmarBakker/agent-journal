from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import OPEN_TASK_LIMIT_SECONDS, Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, subject=AgentRole.MAIN)
@setting(TasksOptions.FIRST_DELAY, 3)
def test_enough_edits_ask_for_a_log_once(story):
    story.repeat(int(story.setting(TasksOptions.FIRST_DELAY)) + 1, lambda: story.agent_writes(story.agents.subject, "a.py"))
    story.last_step.expect_agent_told(story.agents.subject, TasksNudges.LOG_REQUEST)
    result = story.agent_writes(story.agents.subject, "a.py")
    result.expect_agent_not_told(story.agents.subject, TasksNudges.LOG_REQUEST)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
@setting(TasksOptions.FIRST_DELAY, 3)
def test_reads_are_never_counted_as_edits(story):
    result = story.agent_reads(story.agents.subject, count=int(story.setting(TasksOptions.FIRST_DELAY)) + 1)
    result.expect_agent_not_told(story.agents.subject, TasksNudges.LOG_REQUEST)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
@setting(TasksOptions.TASK_REMINDER_INTERVAL, 2)
def test_every_set_number_of_edits_the_task_is_named_back(story):
    story.repeat(int(story.setting(TasksOptions.TASK_REMINDER_INTERVAL)) + 1, lambda: story.agent_writes(story.agents.subject, "a.py"))
    story.last_step.expect_agent_told(story.agents.subject, TasksNudges.CURRENT_TASK_REMINDER)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
@setting(TasksOptions.LOG_LIMIT, 3)
def test_past_the_limit_the_next_write_waits_for_a_log_line(story):
    story.repeat(int(story.setting(TasksOptions.LOG_LIMIT)), lambda: story.agent_writes(story.agents.subject, "a.py"))
    result = story.agent_writes(story.agents.subject, "a.py")
    result.expect_refused(story.agents.subject, TasksNudges.LOG_EDIT_BLOCK)
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.agent_runs(story.agents.subject, f"task log {story.tasks.started} 'the footer has its links'")
    result = story.agent_writes(story.agents.subject, "a.py")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_quiet_quarter_hour_names_the_open_task(story):
    result = story.agent_is_quiet_past(story.agents.subject, OPEN_TASK_LIMIT_SECONDS)
    result.expect_agent_told(story.agents.subject, TasksNudges.OPEN_TASK)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_prompt_leaves_the_task_in_hand(story):
    story.agent_is_prompted(story.agents.subject, "how far is the footer?")
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedPlan, subject=AgentRole.MAIN)
@setting(TasksOptions.FIRST_DELAY, 3)
def test_a_plan_task_is_counted_the_same(story):
    story.repeat(int(story.setting(TasksOptions.FIRST_DELAY)) + 1, lambda: story.agent_writes(story.agents.subject, "a.py"))
    story.last_step.expect_agent_told(story.agents.subject, TasksNudges.LOG_REQUEST)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
