from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.two_workers import TwoWorkers

CONTEXT_PERCENT = 35


@story(TwoWorkers, subject=AgentRole.WORKER)
def test_a_worker_read_by_id_carries_the_context_its_session_reported_and_none_it_did_not(story):
    story.context_reaches(CONTEXT_PERCENT)
    result = story.user_opens(f"/journal/workers?ids={story.agents.subject},{story.agents.workers.second()}")
    result.expect_viewer_rows("rows", "context", [CONTEXT_PERCENT, None])
    story.expect_task(story.tasks.peer, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
