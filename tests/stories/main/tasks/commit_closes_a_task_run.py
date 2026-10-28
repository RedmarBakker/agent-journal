"""Drives git in a throwaway repository of the story's temp folder, so it runs only with JOURNAL_PROCESS_STORIES set, never in the default story run."""
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_commit_naming_the_task_done_closes_it(story):
    story.project_is_a_git_repository()
    commit = f"git -c user.email=story@example.com -c user.name=Story commit --allow-empty -q -m 'the footer' -m 'Journal: tasks done {story.start.started_task}'"
    story.agent_runs_a_command(commit)
    story.agent_has_run_in_the_shell(commit)
    story.expect_agent_told(TasksNudges.COMMIT_CLOSURE)
    story.expect_task(story.start.started_task, state=TaskState.COMPLETED)
    story.expect_stack(Ready)
