from journal.engine.states.void import Void
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_logs_a_line_on_the_task_it_holds(story):
    story.agent_runs(f"task log {story.start.briefed} 'the grammar is read'")
    story.expect_command_passed()
    story.expect_task_logged(story.start.briefed, "the grammar is read")
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_may_not_complete_the_task_it_holds_by_hand(story):
    story.agent_runs(f"task complete {story.start.briefed} --how 'the parser is done'")
    story.expect_command_refused()
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_stops_with_other_tasks_open_and_is_named_no_next_task(story):
    story.main_agent_runs("task create 'the footer'")
    story.agent_stops()
    story.expect_agent_not_told(TasksNudges.NEXT_TASK_STARTED)
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_may_not_read_the_test_load_which_is_the_agents(story):
    story.agent_runs("tests load")
    story.expect_command_refused()
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)
