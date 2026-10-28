from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.briefed_task import BriefedTask


@story(BriefedTask, mode=BUILDER_MODE)
def test_a_dispatch_that_names_no_change_is_refused(story):
    story.agent_runs(f"worker dispatch 'Lady Lovelace' --task {story.start.briefed} --profile journal-medior --model sonnet")
    story.expect_command_refused()
    story.expect_task(story.start.briefed, state=TaskState.OPEN, delegated=False)
    story.expect_stack(Ready)


@story(BriefedTask, mode=BUILDER_MODE)
def test_a_dispatch_on_a_completed_task_is_refused(story):
    story.agent_runs(f"task complete {story.start.briefed} --how done")
    story.agent_runs(f"worker dispatch 'Lady Lovelace' --task {story.start.briefed} --changes 'the parser' --profile journal-medior --model sonnet")
    story.expect_command_refused()
    story.expect_task(story.start.briefed, state=TaskState.COMPLETED)
    story.expect_stack(Ready)
