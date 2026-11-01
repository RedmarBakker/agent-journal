from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered
from tests.stories.fixtures.worker.worker_run_ended import WorkerRunEnded
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_a_job_sent_to_a_worker_still_out_is_refused(story):
    result = story.agent_runs(story.agents.subject, f"worker send {story.agents.workers.first()} 'now the lexer'")
    result.expect_command_refused()
    result.expect_command_text("is still out")
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkerDelivered, subject=AgentRole.MAIN)
def test_a_worker_whose_run_printed_no_session_is_never_sent_a_job(story):
    story.worker_run_ends_printing(story.agents.workers.first(), "plain words")
    result = story.agent_runs(story.agents.subject, f"worker send {story.agents.workers.first()} 'now the lexer'")
    result.expect_command_refused()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkerRunEnded, subject=AgentRole.MAIN)
def test_a_released_worker_is_sent_its_next_job_only_with_a_task_resumes_its_session_on_it_and_the_agent_waits_until_it_reports_again(story):
    lexer = story.agent_creates_task(story.agents.subject, "the lexer")
    story.agent_runs(story.agents.subject, f"worker release {story.agents.workers.first()} --drop")
    result = story.agent_runs(story.agents.subject, f"worker send {story.agents.workers.first()} 'now the lexer'")
    result.expect_command_refused()
    result.expect_command_text(f"journal worker send {story.agents.workers.first()} --task <task>")
    result = story.agent_runs(story.agents.subject, f"worker send {story.agents.workers.first()} 'now the lexer' --task {lexer}")
    result.expect_command_passed()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DISPATCHED, brief="now the lexer", resume=story.session_of(story.agents.workers.first()))
    story.expect_task(lexer, delegated=True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
    story.agent_resumes_the_session(story.agents.workers.first())
    story.agent_clocks_in(story.agents.workers.first())
    story.agent_proves(story.agents.workers.first(), 1, "lexer.py:4, test_splits passes")
    story.agent_clocks_out(story.agents.workers.first(), "the lexer splits the words")
    story.expect_stack(story.agents.subject, Ready)
