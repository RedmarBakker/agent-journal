from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE)
@setting(TasksOptions.PRIORITY_REMIND_TASKS, 2)
def test_tasks_left_at_the_default_priority_are_asked_about(story):
    story.repeat(int(story.setting(TasksOptions.PRIORITY_REMIND_TASKS)), lambda: story.agent_creates_task("more work"))
    story.agent_reads()
    story.expect_agent_told(TasksNudges.PRIORITIES_REMINDER)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
@setting(TasksOptions.PRIORITY_REMIND_TASKS, 2)
def test_tasks_given_a_priority_are_not_asked_about(story):
    story.repeat(int(story.setting(TasksOptions.PRIORITY_REMIND_TASKS)), lambda: story.agent_runs("task create 'more work' --priority high"))
    story.agent_reads()
    story.expect_agent_not_told(TasksNudges.PRIORITIES_REMINDER)
    story.expect_stack(Ready)
