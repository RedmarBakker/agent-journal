from journal.engine.states.void import Void
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.briefed_task import BriefedTask
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_a_worker_clocks_in_only_once_each_time_it_is_sent(story):
    result = story.agent_runs(story.agents.workers.first(), "clock-in")
    result.expect_command_refused()
    story.expect_stack(story.agents.workers.first(), Void, WorkingTask)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(DispatchedWorker, subject=AgentRole.MAIN)
def test_a_worker_whose_task_was_cancelled_before_it_clocked_in_cannot_clock_in(story):
    story.user_cancels_task(story.tasks.briefed, "not needed")
    result = story.agent_runs(story.agents.workers.first(), "clock-in")
    result.expect_command_refused()
    story.expect_task(story.tasks.briefed, state=TaskState.CANCELLED)
    story.expect_stack(story.agents.subject, Ready)


@story(BriefedTask, subject=AgentRole.MAIN)
def test_only_a_worker_clocks_in(story):
    result = story.agent_runs(story.agents.subject, "clock-in")
    result.expect_command_refused()
    story.expect_task(story.tasks.briefed, delegated=False)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_a_clock_out_with_a_point_unproved_is_refused(story):
    story.agent_proves(story.agents.workers.first(), 1, "parser.py:12, test_reads passes")
    result = story.agent_runs(story.agents.workers.first(), "clock-out 'the parser is done'")
    result.expect_command_refused()
    result.expect_agent_not_told(story.agents.subject, WorkersNudges.WORK_READY)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_a_proof_for_a_point_the_brief_does_not_have_is_refused(story):
    result = story.agent_runs(story.agents.workers.first(), "proof 3 'parser.py:40'")
    result.expect_command_refused()
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
