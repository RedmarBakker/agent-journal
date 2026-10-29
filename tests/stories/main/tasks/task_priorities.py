from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(TasksOptions.PRIORITY_REMIND_TASKS, 2)
def test_tasks_left_at_the_default_priority_are_asked_about(story):
    story.repeat(int(story.setting(TasksOptions.PRIORITY_REMIND_TASKS)), lambda: story.agent_creates_task(story.agents.subject, "more work"))
    story.agent_reads(story.agents.subject)
    story.expect_agent_told(story.agents.subject, TasksNudges.PRIORITIES_REMINDER)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(TasksOptions.PRIORITY_REMIND_TASKS, 2)
def test_tasks_given_a_priority_are_not_asked_about(story):
    story.repeat(int(story.setting(TasksOptions.PRIORITY_REMIND_TASKS)), lambda: story.agent_runs(story.agents.subject, "task create 'more work' --priority high"))
    story.agent_reads(story.agents.subject)
    story.expect_agent_not_told(story.agents.subject, TasksNudges.PRIORITIES_REMINDER)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_task_list_puts_the_most_urgent_first_by_name_or_number(story):
    story.agent_runs(story.agents.subject, "task create 'the docs'")
    story.expect_task_made_by(story.agents.subject, story.task_number())
    story.agent_runs(story.agents.subject, "task create 'the outage' --priority critical")
    story.agent_runs(story.agents.subject, "task create 'the odd one' --priority 120")
    story.agent_runs(story.agents.subject, "task list")
    story.expect_command_lines_in_order("the outage", "the odd one", "the docs")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_priority_that_is_no_name_is_refused(story):
    outage = story.agent_creates_task(story.agents.subject, "the outage")
    story.agent_runs(story.agents.subject, f"task edit {outage} --priority soon")
    story.expect_command_text("no such priority: soon")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(TasksOptions.PRIORITY_REMIND_TASKS, 2)
@setting(TasksOptions.PRIORITY_BLOCK_TASKS, 3)
def test_enough_tasks_at_the_default_priority_hold_writes_until_their_priorities_are_set_or_confirmed(story):
    first = story.agent_creates_task(story.agents.subject, "more work")
    story.repeat(int(story.setting(TasksOptions.PRIORITY_BLOCK_TASKS)) - 1, lambda: story.agent_creates_task(story.agents.subject, "more work"))
    story.agent_writes(story.agents.subject, "a.py")
    story.expect_refused(story.agents.subject, TasksNudges.PRIORITIES_REFUSAL)
    story.agent_runs(story.agents.subject, "task create 'urgent work' --priority high")
    story.agent_writes(story.agents.subject, "a.py")
    story.expect_refused(story.agents.subject, TasksNudges.PRIORITIES_REFUSAL)
    story.agent_runs(story.agents.subject, f"task edit {first} --priority low")
    story.agent_runs(story.agents.subject, "task priorities confirm")
    story.agent_writes(story.agents.subject, "a.py")
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)
