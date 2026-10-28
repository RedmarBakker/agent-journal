from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered

WORKER_NAME = "Lady Lovelace"


@story(WorkerDelivered, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_with_work_to_check_is_listed_among_the_workers_to_act_on(story):
    story.agent_runs("worker open")
    story.expect_command_text(WORKER_NAME)
    story.expect_stack(Ready)


@story(DispatchedWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_that_reported_is_left_out_of_the_workers_to_act_on_and_kept_in_the_full_list(story):
    story.agent_runs(f"worker report {story.start.worker} 'the parser reads the grammar'")
    story.agent_runs("worker open")
    story.expect_command_text_without(WORKER_NAME)
    story.agent_runs("worker list")
    story.expect_command_text(WORKER_NAME)
    story.expect_stack(Ready)
