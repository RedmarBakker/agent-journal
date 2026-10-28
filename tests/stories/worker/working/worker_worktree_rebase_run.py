"""Drives git in a throwaway repository of the story's temp folder, so it runs only with JOURNAL_PROCESS_STORIES set, never in the default story run."""
from journal.engine.states.void import Void
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.worktree_worker import WorktreeWorker


@story(WorktreeWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_whose_rebase_waited_is_rebased_at_its_clock_out(story):
    story.main_agent_runs(f"worker rebase {story.start.worker}")
    story.agent_runs("proof 1 'parser.py:12, test_reads passes'")
    story.agent_runs("proof 2 'parser.py:30, test_names passes'")
    story.agent_runs("clock-out 'the parser is done'")
    story.expect_command_passed()
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED, rebase_due=False)
    story.expect_stack(Void)
