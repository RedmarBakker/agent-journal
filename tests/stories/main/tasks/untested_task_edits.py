from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.task_queue import TaskQueue


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_task_blocked_with_untested_edits_is_asked_once_whether_it_only_waits_for_its_tests(story):
    story.agent_writes(story.agents.subject, "footer.py")
    result = story.agent_runs(story.agents.subject, f"task block {story.tasks.started} 'the header comes first'")
    result.expect_agent_told(story.agents.subject, TasksNudges.UNTESTED_TASK_EDITS, n=story.tasks.started)
    story.expect_stack(story.agents.subject, Ready)


@story(TaskQueue, subject=AgentRole.MAIN)
def test_a_task_left_for_another_with_untested_edits_is_asked_about_too(story):
    story.agent_writes(story.agents.subject, "footer.py")
    result = story.agent_runs(story.agents.subject, f"task start {story.tasks.open}")
    result.expect_agent_told(story.agents.subject, TasksNudges.UNTESTED_TASK_EDITS, n=story.tasks.started)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_task_whose_edits_a_test_run_checked_is_set_aside_without_the_question(story):
    story.agent_writes(story.agents.subject, "footer.py")
    story.agent_runs_in_the_shell(story.agents.subject, "pytest -q")
    result = story.agent_runs(story.agents.subject, f"task block {story.tasks.started} 'the header comes first'")
    result.expect_agent_not_told(story.agents.subject, TasksNudges.UNTESTED_TASK_EDITS)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_task_blocked_with_no_edits_is_set_aside_without_the_question(story):
    result = story.agent_runs(story.agents.subject, f"task block {story.tasks.started} 'the header comes first'")
    result.expect_agent_not_told(story.agents.subject, TasksNudges.UNTESTED_TASK_EDITS)
    story.expect_stack(story.agents.subject, Ready)
