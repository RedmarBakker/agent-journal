from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker

WORKER_NAME = "Lady Lovelace"


@story(DispatchedWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_report_reaches_the_agent_that_waited_on_it_ends_the_wait_and_leaves_the_workers_to_act_on(story):
    story.agent_runs(f"worker report {story.start.worker} 'the parser reads the grammar'")
    story.expect_command_passed()
    story.expect_agent_told(WorkersNudges.WORKER_REPORTED, n=story.start.worker)
    story.expect_worker(story.start.worker, state=WorkerState.REPORTED)
    story.agent_runs("worker open")
    story.expect_command_text_without(WORKER_NAME)
    story.agent_runs("worker list")
    story.expect_command_text(WORKER_NAME)
    story.expect_stack(Ready)
