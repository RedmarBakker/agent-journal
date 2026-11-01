from journal.engine.states.void import Void
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_the_user_completing_a_workers_task_releases_the_worker_and_tells_it_to_stop(story):
    result = story.user_completes_task(story.tasks.briefed, "done by hand")
    story.expect_worker(story.agents.workers.first(), state=WorkerState.RELEASED)
    result.expect_agent_told(story.agents.subject, WorkersNudges.USER_CLOSURE, task=story.tasks.briefed)
    story.expect_stack(story.agents.subject, Void)
