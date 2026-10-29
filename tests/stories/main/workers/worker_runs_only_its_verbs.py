from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_may_not_create_a_task(story):
    story.agent_runs(story.agents.workers.first(), "task create 'more work'")
    story.expect_command_refused()
    story.expect_task_count(1)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_may_not_create_a_plan(story):
    story.agent_runs(story.agents.workers.first(), "plan create p --brief b")
    story.expect_command_refused()
    story.expect_plan_count(0)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_may_not_send_a_message_to_the_user(story):
    story.agent_runs(story.agents.workers.first(), "message send hello")
    story.expect_command_refused()
    story.expect_agent_messages(0)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_may_not_change_a_setting(story):
    story.agent_runs(story.agents.workers.first(), "settings set tasks.auto off")
    story.expect_command_refused()
    story.expect_setting(TasksOptions.AUTO, True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_may_not_ask_the_user_a_question(story):
    story.agent_runs(story.agents.workers.first(), "question ask 'go on?' --options yes no")
    story.expect_command_refused()
    story.expect_question_count(0)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_may_run_its_own_verbs(story):
    story.agent_runs_cleanly(story.agents.workers.first(), f"task show {story.tasks.briefed}")
    story.agent_runs_cleanly(story.agents.workers.first(), "todo add 'read the parser'")
    story.agent_runs_cleanly(story.agents.workers.first(), "proof 1 'parser.py:12, test_reads passes'")
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_may_not_dispatch_a_worker(story):
    story.agent_runs(story.agents.workers.first(), f"worker dispatch 'Mr. Babbage' --task {story.tasks.briefed} --changes 'the parser' --profile journal-medior --model sonnet")
    story.expect_command_refused()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
