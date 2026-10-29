from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.orchestrator_worker import OrchestratorWorker
from tests.stories.fixtures.main.orchestrator_worker_delivered import OrchestratorWorkerDelivered
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


@story(OrchestratorWorkerDelivered, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_an_orchestrator_stop_with_work_waiting_to_be_checked_is_refused(story):
    story.agent_stops(story.agents.subject)
    story.expect_refused(story.agents.subject, WorkersNudges.DELIVERED_WAITING)
    story.expect_stack(story.agents.subject, Orchestrating)


@story(WorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_builder_stop_with_work_waiting_to_be_checked_is_not_held_for_it(story):
    story.agent_stops(story.agents.subject)
    story.expect_agent_not_told(story.agents.subject, WorkersNudges.DELIVERED_WAITING)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)
    story.expect_stack(story.agents.subject, Ready)


@story(OrchestratorWorker, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_an_orchestrator_that_waits_on_its_worker_may_stop(story):
    story.agent_runs(story.agents.subject, f"worker wait {story.agents.workers.first()}")
    story.agent_stops(story.agents.subject)
    story.expect_agent_not_told(story.agents.subject, WorkersNudges.ACTIVE_WORKERS)
    story.expect_stack(story.agents.subject, Orchestrating, ExternalWait)


@story(OrchestratorWorker, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_an_orchestrator_stop_with_a_worker_out_is_held_once(story):
    story.agent_stops(story.agents.subject)
    story.expect_refused(story.agents.subject, WorkersNudges.ACTIVE_WORKERS, numbers=str(story.agents.workers.first()))
    story.agent_stops_again(story.agents.subject)
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Orchestrating)
