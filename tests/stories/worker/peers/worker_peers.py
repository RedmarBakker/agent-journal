from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.two_workers import TwoWorkers

PEER_NAME = "Mr. Babbage"


@story(TwoWorkers, subject=AgentRole.WORKER)
def test_a_worker_lists_the_other_workers_of_its_dispatcher(story):
    result = story.agent_runs(story.agents.subject, "worker peers")
    result.expect_command_passed()
    result.expect_command_text(PEER_NAME)
    result.expect_command_text("journal worker notify")
    result.expect_command_text_without("Lady Lovelace")
    story.expect_worker(story.agents.workers.second(), state=WorkerState.READY)
    story.expect_task(story.tasks.peer, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(TwoWorkers, subject=AgentRole.WORKER)
def test_a_worker_sending_a_job_to_a_peer_still_out_is_refused(story):
    result = story.agent_runs(story.agents.subject, f"worker send {story.agents.workers.second()} 'print the errors too'")
    result.expect_command_refused()
    story.expect_worker(story.agents.workers.second(), state=WorkerState.READY)
    story.expect_task(story.tasks.peer, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(TwoWorkers, subject=AgentRole.WORKER)
def test_a_worker_may_not_send_itself_a_word(story):
    result = story.agent_runs(story.agents.subject, f"worker notify {story.agents.workers.first()} 'remember the grammar'")
    result.expect_command_refused()
    story.expect_worker(story.agents.workers.second(), state=WorkerState.READY)
    story.expect_task(story.tasks.peer, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)



@story(TwoWorkers, subject=AgentRole.WORKER)
def test_a_worker_may_not_change_a_peers_model(story):
    result = story.agent_runs(story.agents.subject, f"worker send {story.agents.workers.second()} 'print the errors too' --model opus")
    result.expect_command_refused()
    result.expect_command_text("only the agent that dispatched a worker changes its model")
    story.expect_task(story.tasks.peer, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(TwoWorkers, subject=AgentRole.WORKER)
def test_a_worker_may_not_report_for_a_peer(story):
    result = story.agent_runs(story.agents.subject, f"worker report {story.agents.workers.second()} 'the lexer is done'")
    result.expect_command_refused()
    result.expect_command_text("a worker reports for itself")
    story.expect_task(story.tasks.peer, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
