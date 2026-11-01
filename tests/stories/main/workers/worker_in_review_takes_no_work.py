from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


@story(WorkerDelivered, subject=AgentRole.MAIN)
def test_a_worker_whose_work_waits_for_its_check_is_queued_nothing_and_sent_no_job(story):
    docs = story.agent_creates_task(story.agents.subject, "the docs")
    result = story.agent_runs(story.agents.subject, f"worker queue {story.agents.workers.first()} {docs}")
    result.expect_command_refused()
    result.expect_command_text("waits for its merge")
    result = story.agent_runs(story.agents.subject, f"worker send {story.agents.workers.first()} --task {docs} 'write the docs'")
    result.expect_command_refused()
    result.expect_command_text("waits for its merge")
    story.expect_task(docs, delegated=False)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)
    story.expect_stack(story.agents.subject, Ready)
