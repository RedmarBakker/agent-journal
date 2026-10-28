from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(TasksOptions.PRIORITY_REMIND_TASKS, 2)
def test_tasks_left_at_the_default_priority_are_asked_about(story):
    story.repeat(int(story.setting(TasksOptions.PRIORITY_REMIND_TASKS)), lambda: story.agent_creates_task("more work"))
    story.agent_reads()
    story.expect_agent_told(TasksNudges.PRIORITIES_REMINDER)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(TasksOptions.PRIORITY_REMIND_TASKS, 2)
def test_tasks_given_a_priority_are_not_asked_about(story):
    story.repeat(int(story.setting(TasksOptions.PRIORITY_REMIND_TASKS)), lambda: story.agent_runs("task create 'more work' --priority high"))
    story.agent_reads()
    story.expect_agent_not_told(TasksNudges.PRIORITIES_REMINDER)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_task_list_puts_the_most_urgent_first_by_name_or_number(story):
    story.agent_runs("task create 'the docs'")
    story.agent_runs("task create 'the outage' --priority critical")
    story.agent_runs("task create 'the odd one' --priority 120")
    story.agent_runs("task list")
    story.expect_command_lines_in_order("the outage", "the odd one", "the docs")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_priority_that_is_no_name_is_refused(story):
    outage = story.agent_creates_task("the outage")
    story.agent_runs(f"task edit {outage} --priority soon")
    story.expect_command_text("no such priority: soon")
    story.expect_stack(Ready)
