from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_a_worker_start_pauses_no_task_of_the_main_agent(story):
    story.agent_starts_a_session(story.agents.subject)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
