from journal.engine.states.void import Void
from journal.features.tasks.tasks_conduct import POLL_REPEAT_COMMANDS
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.working_worker import WorkingWorker

POLLED_OUTPUT = 1


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_may_list_its_outputs(story):
    story.agent_runs("output list")
    story.expect_command_passed()
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
@setting(FOREGROUND_OPTION, 1)
def test_a_worker_stopping_with_its_own_output_running_is_refused_with_its_number(story):
    output = story.agent_runs_a_command(f"sleep {story.setting(FOREGROUND_OPTION) * 2}")
    story.agent_stops()
    story.expect_refused(WorkersNudges.OUTPUT_UNFINISHED, n=output)
    story.background_run_ends(output)
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)
