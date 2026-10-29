from journal.engine.engine_nudges import EngineNudges
from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(DispatchedWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_that_writes_before_it_clocks_in_is_refused(story):
    story.agent_writes(story.agents.subject, "parser.py")
    story.expect_refused(story.agents.subject, EngineNudges.JOBLESS_HELPER)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DISPATCHED)
    story.expect_stack(story.agents.subject, Void)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_stop_with_open_todos_is_told_them(story):
    story.agent_runs(story.agents.subject, "todo add 'read the grammar'")
    story.agent_stops(story.agents.subject)
    story.expect_agent_told(story.agents.subject, WorkersNudges.OPEN_TODOS, count=1)
    story.expect_task(story.fixture.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_stop_with_every_todo_checked_is_told_nothing_of_them(story):
    story.agent_runs(story.agents.subject, "todo add 'read the grammar'")
    story.agent_runs(story.agents.subject, "todo check 1")
    story.agent_stops(story.agents.subject)
    story.expect_agent_not_told(story.agents.subject, WorkersNudges.OPEN_TODOS)
    story.expect_task(story.fixture.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_never_runs_git(story):
    story.agent_runs_in_the_shell(story.agents.subject, "git commit -am done")
    story.expect_refused(story.agents.subject, WorkersNudges.WORKER_GIT_REFUSAL)
    story.expect_task(story.fixture.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_workers_to_do_list_reads_back_in_order_with_its_checked_item(story):
    story.agent_runs(story.agents.subject, "todo add 'write the grammar'")
    story.agent_runs(story.agents.subject, "todo add 'write the test'")
    story.agent_runs(story.agents.subject, "todo add 'run it'")
    story.agent_runs(story.agents.subject, "todo check 2")
    story.agent_runs(story.agents.subject, "todo check 7")
    story.expect_command_text("has 3 items")
    story.agent_runs(story.agents.subject, "todo list")
    story.expect_command_lines_in_order("[ ]  write the grammar", "[x]  write the test", "[ ]  run it")
    story.agent_runs(story.agents.main, "todo list")
    story.expect_command_refused()
    story.expect_stack(story.agents.subject, Void, WorkingTask)

