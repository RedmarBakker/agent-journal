from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.two_workers import TwoWorkers

PEER_NAME = "Mr. Babbage"


@story(TwoWorkers, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_lists_the_other_workers_of_its_dispatcher(story):
    story.agent_runs("worker peers")
    story.expect_command_passed()
    story.expect_command_text(PEER_NAME)
    story.expect_worker(story.start.peer, state=WorkerState.READY)
    story.expect_task(story.start.peer_task, delegated=True)
    story.expect_stack(Void, WorkingTask)


@story(TwoWorkers, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_sending_a_job_to_a_peer_still_out_is_refused(story):
    story.agent_runs(f"worker send {story.start.peer} 'print the errors too'")
    story.expect_command_refused()
    story.expect_worker(story.start.peer, state=WorkerState.READY)
    story.expect_task(story.start.peer_task, delegated=True)
    story.expect_stack(Void, WorkingTask)


@story(TwoWorkers, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_may_not_send_itself_a_word(story):
    story.agent_runs(f"worker notify {story.start.worker} 'remember the grammar'")
    story.expect_command_refused()
    story.expect_worker(story.start.peer, state=WorkerState.READY)
    story.expect_task(story.start.peer_task, delegated=True)
    story.expect_stack(Void, WorkingTask)
