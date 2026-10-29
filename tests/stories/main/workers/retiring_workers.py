from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


@story(DispatchedWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_retiring_a_worker_still_out_is_never_asked_whether_it_could_be_reused(story):
    story.agent_runs_in_the_shell(story.agents.subject, f"journal worker stop {story.agents.workers.first()}")
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
