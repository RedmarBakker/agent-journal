from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker


@story(DispatchedWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_report_reaches_the_agent_that_waited_on_it_and_ends_the_wait(story):
    story.agent_runs(f"worker report {story.start.worker} 'the parser reads the grammar'")
    story.expect_command_passed()
    story.expect_agent_told(WorkersNudges.WORKER_REPORTED, n=story.start.worker)
    story.expect_worker(story.start.worker, state=WorkerState.REPORTED)
    story.expect_stack(Ready)
