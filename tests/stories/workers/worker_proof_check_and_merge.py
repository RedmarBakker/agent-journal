from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_conduct import STRUGGLE_REJECTIONS
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.clocked_in_worker import ClockedInWorker
from tests.stories.fixtures.worker_delivered import WorkerDelivered


@story(WorkerDelivered, end=[Ready])
def test_checked_proofs_let_the_work_be_merged(story):
    story.agent_runs(f"worker check {story.start.worker} 1")
    story.agent_runs(f"worker check {story.start.worker} 2")
    story.agent_runs(f"worker merge {story.start.worker}")
    story.expect_command_passed()
    story.expect_task(story.start.briefed, state=TaskState.COMPLETED)


@story(WorkerDelivered, end=[Ready])
def test_a_merge_with_an_unchecked_point_is_refused(story):
    story.agent_runs(f"worker merge {story.start.worker}")
    story.expect_command_refused()
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
    story.expect_task(story.start.briefed, delegated=True)


@story(WorkerDelivered, end=[Ready])
def test_a_proof_checked_short_sends_the_worker_back_on_its_point(story):
    story.agent_runs(f"worker check {story.start.worker} 1 --short 'no test reads the grammar'")
    story.expect_command_passed()
    story.expect_agent_told(WorkersNudges.PROOF_REJECTED, n=story.start.worker, point=1)
    story.expect_task(story.start.briefed, delegated=True)


@story(WorkerDelivered, end=[Ready])
def test_a_point_sent_back_again_names_the_earlier_reason(story):
    story.agent_runs(f"worker check {story.start.worker} 1 --short 'no test reads the grammar'")
    story.worker_proves(story.start.worker, 1, "parser.py:12, test_grammar passes")
    story.agent_runs(f"worker check {story.start.worker} 1 --short 'the test is empty'")
    story.expect_agent_told(WorkersNudges.PROOF_REJECTED_REPEAT, n=story.start.worker, point=1)


@story(WorkerDelivered, end=[Ready])
def test_a_point_sent_back_often_names_a_stronger_model(story):
    for _ in range(STRUGGLE_REJECTIONS - 1):
        story.agent_runs(f"worker check {story.start.worker} 1 --short 'still short'")
        story.worker_proves(story.start.worker, 1, "parser.py:12, test_grammar passes")
    story.agent_runs(f"worker check {story.start.worker} 1 --short 'still short'")
    story.expect_agent_told(WorkersNudges.PROOF_REJECTED_OFTEN, point=1, times=STRUGGLE_REJECTIONS)


@story(WorkerDelivered, end=[Ready])
def test_a_check_of_a_point_the_worker_has_not_proved_again_is_refused(story):
    story.agent_runs(f"worker check {story.start.worker} 1 --short 'no test reads the grammar'")
    story.agent_runs(f"worker check {story.start.worker} 1")
    story.expect_command_refused()
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_merge_of_a_worker_that_has_not_clocked_out_is_refused(story):
    story.agent_runs(f"worker merge {story.start.worker}")
    story.expect_command_refused()
    story.expect_worker(story.start.worker, state=WorkerState.READY)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_merging_every_waiting_worker_with_none_waiting_is_refused(story):
    story.agent_runs("worker merge --all")
    story.expect_command_refused()
    story.expect_task(story.start.briefed, delegated=True)


@story(WorkerDelivered, end=[Ready])
def test_a_worker_with_unmerged_work_is_released_only_with_drop(story):
    story.agent_runs(f"worker release {story.start.worker}")
    story.expect_command_refused()
    story.agent_runs(f"worker release {story.start.worker} --drop")
    story.expect_command_passed()
    story.expect_task(story.start.briefed, delegated=False)
