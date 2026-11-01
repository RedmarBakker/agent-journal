from journal.engine.states.void import Void
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.states.working_task import WorkingTask
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_a_worker_logs_a_line_on_the_task_it_holds(story):
    result = story.agent_runs(story.agents.subject, f"task log {story.tasks.briefed} 'the grammar is read'")
    result.expect_command_passed()
    story.expect_task_logged(story.tasks.briefed, "the grammar is read")
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_a_worker_may_not_complete_the_task_it_holds_by_hand(story):
    result = story.agent_runs(story.agents.subject, f"task complete {story.tasks.briefed} --how 'the parser is done'")
    result.expect_command_refused()
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_a_worker_stops_with_other_tasks_open_and_is_named_no_next_task(story):
    story.agent_runs(story.agents.main, "task create 'the footer'")
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, TasksNudges.NEXT_TASK_STARTED)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, subject=AgentRole.WORKER)
def test_a_worker_may_not_read_the_test_load_which_is_the_agents(story):
    result = story.agent_runs(story.agents.subject, "tests load")
    result.expect_command_refused()
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
