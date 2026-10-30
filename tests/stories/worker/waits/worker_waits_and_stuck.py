from journal.engine.states.void import Void
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.impasse import Impasse
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_that_awaits_waits_over_its_work_until_its_own_tool_use(story):
    result = story.agent_runs(story.agents.subject, "await 'the build of the parser' --until false")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Void, WorkingTask, ExternalWait)
    story.agent_reads(story.agents.subject)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_workers_wait_on_its_own_command_ends_when_the_command_does(story):
    output = story.agent_has_a_background_run_printing(story.agents.subject, "./scripts/build.sh")
    story.agent_runs(story.agents.subject, f"await 'the build of the parser' --output {output}")
    story.expect_stack(story.agents.subject, Void, WorkingTask, ExternalWait)
    story.background_run_ends(story.agents.subject, output, "built")
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_journal_command_leaves_the_workers_wait(story):
    story.agent_runs(story.agents.subject, "await 'the build of the parser' --until false")
    story.agent_runs(story.agents.subject, "todo add 'read the grammar'")
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_clearing_its_wait_is_back_at_its_work(story):
    story.agent_runs(story.agents.subject, "await 'the build of the parser' --until false")
    result = story.agent_runs(story.agents.subject, "await clear")
    result.expect_command_passed()
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_that_says_it_is_stuck_waits_until_its_next_tool_use(story):
    story.agent_runs(story.agents.subject, "stuck 'the grammar file is missing'")
    story.expect_stack(story.agents.subject, Void, WorkingTask, Impasse)
    story.agent_reads(story.agents.subject)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
