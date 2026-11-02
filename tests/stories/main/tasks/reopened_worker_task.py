from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.reopened_worker_task import ReopenedWorkerTask
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(ReopenedWorkerTask, subject=AgentRole.MAIN)
def test_a_reopened_merged_task_lets_the_main_agent_start_another_task(story):
    task = story.tasks.briefed
    story.expect_task(task, state=TaskState.OPEN, delegated=False)
    story.expect_task_unheld(task)
    other = story.agent_creates_briefed_task(story.agents.main, "the footer", "write the footer")
    started = story.agent_runs(story.agents.main, f"task start {other}")
    started.expect_command_passed()
    story.expect_task(other, state=TaskState.STARTED, delegated=False)
    story.expect_stack(story.agents.main, Ready, Working)


@story(ReopenedWorkerTask, subject=AgentRole.MAIN)
def test_a_reopened_merged_task_blocked_again_does_not_hold_the_main_agent(story):
    task = story.tasks.briefed
    blocked = story.user_blocks_task(task, "the owner needs time")
    blocked.expect_viewer_passed()
    story.expect_task(task, state=TaskState.BLOCKED, delegated=False)
    story.expect_task_unheld(task)
    other = story.agent_creates_briefed_task(story.agents.main, "the header", "write the header")
    started = story.agent_runs(story.agents.main, f"task start {other}")
    started.expect_command_passed()
    story.expect_task(other, state=TaskState.STARTED, delegated=False)
    story.expect_stack(story.agents.main, Ready, Working)


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_a_task_completed_by_the_user_leaves_its_worker_and_no_delegation(story):
    task = story.tasks.briefed
    completed = story.user_completes_task(task, "the owner finished it")
    completed.expect_viewer_passed()
    story.expect_task(task, state=TaskState.COMPLETED, delegated=False)
    story.expect_task_unheld(task)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.RELEASED)
    other = story.agent_creates_briefed_task(story.agents.main, "the index", "write the index")
    started = story.agent_runs(story.agents.main, f"task start {other}")
    started.expect_command_passed()
    story.expect_stack(story.agents.main, Ready, Working)
