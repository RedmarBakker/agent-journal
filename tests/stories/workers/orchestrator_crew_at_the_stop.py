from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_nudges import WorkersNudges
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.orchestrator_clocked_in_worker import OrchestratorClockedInWorker
from tests.stories.fixtures.orchestrator_worker_delivered import OrchestratorWorkerDelivered
from tests.stories.fixtures.worker_delivered import WorkerDelivered


@story(OrchestratorWorkerDelivered, end=[Orchestrating])
def test_an_orchestrator_stop_with_work_waiting_to_be_checked_is_refused(story):
    story.agent_stops()
    story.expect_refused(WorkersNudges.DELIVERED_WAITING)


@story(WorkerDelivered, end=[Ready])
def test_a_builder_stop_with_work_waiting_to_be_checked_is_not_held_for_it(story):
    story.agent_stops()
    story.expect_agent_not_told(WorkersNudges.DELIVERED_WAITING)


@story(OrchestratorClockedInWorker, end=[Orchestrating, ExternalWait])
def test_an_orchestrator_waiting_on_its_worker_may_stop(story):
    story.agent_stops()
    story.expect_agent_not_told(WorkersNudges.ACTIVE_WORKERS)


@story(OrchestratorClockedInWorker, end=[Orchestrating])
def test_an_orchestrator_working_beside_its_worker_is_held_once_at_the_stop(story):
    story.agent_writes("notes.md")
    story.agent_stops()
    story.expect_refused(WorkersNudges.ACTIVE_WORKERS, numbers=str(story.start.worker))
    story.agent_stops()
    story.expect_allowed()
