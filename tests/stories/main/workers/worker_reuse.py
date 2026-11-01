from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.worker_run_ended import WorkerRunEnded


@story(WorkerRunEnded, subject=AgentRole.MAIN)
def test_each_send_counts_one_reuse_a_stopped_worker_sent_again_is_out_and_the_retire_keeps_its_reason(story):
    worker = story.agents.workers.first()
    story.agent_runs(story.agents.subject, f"worker send {worker} 'the aliases too'")
    story.agent_runs(story.agents.subject, f"worker stop {worker} --why 'the aliases need a new design'")
    result = story.agent_runs(story.agents.subject, f"worker send {worker} 'the aliases, redesigned'")
    result.expect_command_passed()
    story.expect_worker(worker, state=WorkerState.DISPATCHED, reuse_count=2)
    result = story.agent_runs(story.agents.subject, "worker list")
    result.expect_command_text("dispatched")
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
