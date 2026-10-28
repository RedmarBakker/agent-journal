from journal.engine.states.compacting import Compacting
from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_compacting_is_held_and_then_back_at_its_work_still_clocked_in(story):
    story.compaction_begins()
    story.expect_stack(Void, WorkingTask, Compacting)
    story.compacted_session_starts()
    story.agent_runs("proof 1 'parser.py:12, test_reads passes'")
    story.expect_command_passed()
    story.expect_worker(story.start.worker, state=WorkerState.READY)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_session_ending_before_clock_out_leaves_it_ended_on_its_work(story):
    story.agent_ends_the_session()
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask, Ended)


@story(WorkerDelivered, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_session_ending_after_clock_out_keeps_it_delivered(story):
    story.agent_ends_the_session()
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
    story.expect_stack(Void, Ended)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_prompt_to_the_worker_leaves_its_stack(story):
    story.agent_is_prompted("the dispatcher asks how far the parser is")
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)
