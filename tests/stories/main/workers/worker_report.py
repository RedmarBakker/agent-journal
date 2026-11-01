from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker

WORKER_NAME = "Lady Lovelace"


@story(DispatchedWorker, subject=AgentRole.MAIN)
def test_a_worker_report_reaches_the_agent_that_waited_on_it_ends_the_wait_and_leaves_the_workers_to_act_on(story):
    result = story.agent_runs(story.agents.subject, f"worker report {story.agents.workers.first()} 'the parser reads the grammar'")
    result.expect_command_passed()
    result.expect_agent_told(story.agents.subject, WorkersNudges.WORKER_REPORTED, n=story.agents.workers.first())
    story.expect_worker(story.agents.workers.first(), state=WorkerState.REPORTED)
    result = story.agent_runs(story.agents.subject, "worker open")
    result.expect_command_text_without(WORKER_NAME)
    result = story.agent_runs(story.agents.subject, "worker list")
    result.expect_command_text(WORKER_NAME)
    story.expect_stack(story.agents.subject, Ready)
