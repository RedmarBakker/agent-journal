from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_may_not_create_a_task(story):
    story.worker_tries(story.start.worker, "task create 'more work'")
    story.expect_command_refused()
    story.expect_task_count(1)
    story.expect_stack(Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_may_not_create_a_plan(story):
    story.worker_tries(story.start.worker, "plan create p --brief b")
    story.expect_command_refused()
    story.expect_plan_count(0)
    story.expect_stack(Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_may_not_send_a_message_to_the_user(story):
    story.worker_tries(story.start.worker, "message send hello")
    story.expect_command_refused()
    story.expect_agent_messages(0)
    story.expect_stack(Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_may_not_change_a_setting(story):
    story.worker_tries(story.start.worker, "settings set tasks.auto off")
    story.expect_command_refused()
    story.expect_setting(TasksOptions.AUTO, True)
    story.expect_stack(Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_may_not_ask_the_user_a_question(story):
    story.worker_tries(story.start.worker, "question ask 'go on?' --options yes no")
    story.expect_command_refused()
    story.expect_question_count(0)
    story.expect_stack(Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_may_run_its_own_verbs(story):
    story.worker_runs(story.start.worker, f"task show {story.start.briefed}")
    story.worker_runs(story.start.worker, "todo add 'read the parser'")
    story.worker_runs(story.start.worker, "proof 1 'parser.py:12, test_reads passes'")
    story.expect_worker(story.start.worker, state=WorkerState.READY)
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_worker_may_not_dispatch_a_worker(story):
    story.worker_tries(story.start.worker, f"worker dispatch 'Mr. Babbage' --task {story.start.briefed} --changes 'the parser' --profile journal-medior --model sonnet")
    story.expect_command_refused()
    story.expect_worker(story.start.worker, state=WorkerState.READY)
    story.expect_stack(Ready, ExternalWait)
