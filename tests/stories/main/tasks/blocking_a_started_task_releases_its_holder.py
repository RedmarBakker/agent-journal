from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, subject=AgentRole.MAIN)
def test_blocking_a_started_task_releases_its_holder_and_unblock_leaves_it_free(story):
    task = story.tasks.started
    blocked = story.user_blocks_task(task, "the owner needs time")
    blocked.expect_viewer_passed()
    story.expect_task(task, state=TaskState.BLOCKED)
    story.expect_task_unheld(task)
    story.expect_stack(story.agents.subject, Ready)

    unblocked = story.user_did(f"/journal/tasks/{task}/unblock", {}, "user reopens the task")
    unblocked.expect_viewer_passed()
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_task_unheld(task)
    story.expect_stack(story.agents.subject, Ready)
