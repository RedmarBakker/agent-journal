from journal.engine.states.void import Void
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_logs_a_line_on_the_task_it_holds(story):
    story.agent_runs(story.agents.subject, f"task log {story.fixture.briefed} 'the grammar is read'")
    story.expect_command_passed()
    story.expect_task_logged(story.fixture.briefed, "the grammar is read")
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_may_not_complete_the_task_it_holds_by_hand(story):
    story.agent_runs(story.agents.subject, f"task complete {story.fixture.briefed} --how 'the parser is done'")
    story.expect_command_refused()
    story.expect_task(story.fixture.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_stops_with_other_tasks_open_and_is_named_no_next_task(story):
    story.agent_runs(story.agents.main, "task create 'the footer'")
    story.agent_stops(story.agents.subject)
    story.expect_agent_not_told(story.agents.subject, TasksNudges.NEXT_TASK_STARTED)
    story.expect_task(story.fixture.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_may_not_read_the_test_load_which_is_the_agents(story):
    story.agent_runs(story.agents.subject, "tests load")
    story.expect_command_refused()
    story.expect_task(story.fixture.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
