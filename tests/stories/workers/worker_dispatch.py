from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.briefed_task import BriefedTask


@story(BriefedTask, end=[Ready, ExternalWait])
def test_a_worker_sent_on_an_open_task_holds_it_and_the_agent_waits_on_it(story):
    worker = story.agent_dispatches_worker("Lady Lovelace", story.start.briefed)
    story.expect_worker(worker, state=WorkerState.DISPATCHED)
    story.expect_task(story.start.briefed, delegated=True)


@story(BriefedTask, end=[Ready])
def test_a_dispatch_that_names_no_change_is_refused(story):
    story.agent_runs(f"worker dispatch 'Lady Lovelace' --task {story.start.briefed} --profile journal-medior --model sonnet")
    story.expect_command_refused()
    story.expect_task(story.start.briefed, state=TaskState.OPEN, delegated=False)


@story(BriefedTask, end=[Ready])
def test_a_dispatch_on_a_completed_task_is_refused(story):
    story.agent_runs(f"task complete {story.start.briefed} --how done")
    story.agent_runs(f"worker dispatch 'Lady Lovelace' --task {story.start.briefed} --changes 'the parser' --profile journal-medior --model sonnet")
    story.expect_command_refused()
    story.expect_task(story.start.briefed, state=TaskState.COMPLETED)
