from journal.engine.engine_nudges import EngineNudges
from journal.engine.states.void import Void
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


@story(DispatchedWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_before_it_clocks_in_is_refused_a_read_and_told_it_has_no_job(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, EngineNudges.JOBLESS_HELPER)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DISPATCHED)
    story.expect_stack(story.agents.subject, Void)


@story(DispatchedWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_journal_command_before_clock_in_goes_through(story):
    result = story.agent_runs(story.agents.subject, "todo list")
    result.expect_command_passed()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DISPATCHED)
    story.expect_stack(story.agents.subject, Void)


@story(DispatchedWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_before_clock_in_is_never_told_the_main_agents_lines(story):
    message = story.user_sends_message("how far is the parser?")
    result = story.agent_runs(story.agents.main, f"message read {message}")
    result.expect_agent_told(story.agents.main, MessagesNudges.MESSAGE_READ)
    result.expect_agent_not_told(story.agents.subject, MessagesNudges.MESSAGE_READ)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DISPATCHED)
    story.expect_stack(story.agents.subject, Void)


@story(DispatchedWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_before_clock_in_cannot_ask_the_user_a_question(story):
    result = story.agent_runs(story.agents.subject, "question ask 'go on?' --options 'the worker goes on' 'the worker stops'")
    result.expect_command_refused()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DISPATCHED)
    story.expect_stack(story.agents.subject, Void)


@story(WorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_that_clocked_out_is_back_on_its_floor_and_refused_again(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, EngineNudges.JOBLESS_HELPER)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)
    story.expect_stack(story.agents.subject, Void)
