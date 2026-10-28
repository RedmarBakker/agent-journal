from journal.engine.engine_nudges import EngineNudges
from journal.engine.states.locked_out import STEADY, LockedOut
from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.lockout_option import LOCKOUT_OPTION
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_whose_journal_came_back_is_held_with_the_wait_line(story):
    story.agent_reads_after_the_journal_was_down(story.setting(LOCKOUT_OPTION) / 2)
    story.expect_refused(EngineNudges.LOCKOUT_WAIT)
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask, LockedOut)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_whose_journal_was_down_past_the_grace_is_told_to_end(story):
    story.agent_reads_after_the_journal_was_down(story.setting(LOCKOUT_OPTION) * 2)
    story.expect_refused(EngineNudges.LOCKOUT_END, grace=story.setting(LOCKOUT_OPTION))
    story.agent_is_quiet_past(STEADY.amount)
    story.agent_reads()
    story.expect_refused(EngineNudges.LOCKOUT_END, grace=story.setting(LOCKOUT_OPTION))
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask, LockedOut)
