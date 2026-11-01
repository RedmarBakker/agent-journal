from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_a_worker_resize_proposal_is_visible_without_changing_the_current_task_size(story):
    task = story.tasks.briefed
    result = story.agent_runs(story.agents.subject, f"task propose-size {task} 5 --reason 'the integration requires another test path'")
    result.expect_command_passed()
    result = story.user_opens(f"/journal/tasks/{task}/size")
    result.expect_viewer_shows("current_size", None)
    result.expect_viewer_rows("proposal_history", "change_type", ["resize_proposal"])
    result.expect_viewer_part(("proposal_history", 0, "size"), 5)
    result.expect_viewer_part(("proposal_history", 0, "reason"), "the integration requires another test path")
    story.expect_task(task, size=None, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
