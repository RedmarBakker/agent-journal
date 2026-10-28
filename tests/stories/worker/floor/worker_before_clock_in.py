from journal.engine.engine_nudges import EngineNudges
from journal.engine.states.void import Void
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


@story(DispatchedWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_before_it_clocks_in_is_refused_a_read_and_told_it_has_no_job(story):
    story.agent_reads()
    story.expect_refused(EngineNudges.JOBLESS_HELPER)
    story.expect_worker(story.start.worker, state=WorkerState.DISPATCHED)
    story.expect_stack(Void)


@story(DispatchedWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_journal_command_before_clock_in_goes_through(story):
    story.agent_runs("todo list")
    story.expect_command_passed()
    story.expect_worker(story.start.worker, state=WorkerState.DISPATCHED)
    story.expect_stack(Void)


@story(DispatchedWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_before_clock_in_is_never_told_the_main_agents_lines(story):
    message = story.user_sends_message("how far is the parser?")
    story.main_agent_runs(f"message read {message}")
    story.expect_main_told(MessagesNudges.MESSAGE_READ)
    story.expect_agent_not_told(MessagesNudges.MESSAGE_READ)
    story.expect_worker(story.start.worker, state=WorkerState.DISPATCHED)
    story.expect_stack(Void)


@story(DispatchedWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_before_clock_in_cannot_ask_the_user_a_question(story):
    story.agent_runs("question ask 'go on?' --options 'the worker goes on' 'the worker stops'")
    story.expect_command_refused()
    story.expect_worker(story.start.worker, state=WorkerState.DISPATCHED)
    story.expect_stack(Void)


@story(WorkerDelivered, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_that_clocked_out_is_back_on_its_floor_and_refused_again(story):
    story.agent_reads()
    story.expect_refused(EngineNudges.JOBLESS_HELPER)
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
    story.expect_stack(Void)
