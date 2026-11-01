from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.worker_run_ended import WorkerRunEnded


@story(WorkerRunEnded, subject=AgentRole.MAIN)
def test_the_user_checks_sends_back_and_merges_a_workers_work_from_the_viewer(story):
    worker = story.agents.workers.first()
    result = story.user_presses(f"/journal/workers/{worker}/check", {"point": 1})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/workers/{worker}/short_check", {"point": 2, "shortfall": "the aliases are missing"})
    result.expect_viewer_passed()
    story.expect_worker(worker, state=WorkerState.DISPATCHED)
    story.agent_resumes_the_session(worker)
    story.agent_clocks_in(worker)
    story.agent_proves(worker, 2, "parser.py:41, the aliases are in")
    story.agent_clocks_out(worker, "the aliases are in")
    story.user_presses(f"/journal/workers/{worker}/check", {"point": 2})
    result = story.user_presses(f"/journal/workers/{worker}/merge", {})
    result.expect_viewer_passed()
    story.expect_task(story.tasks.briefed, state=TaskState.COMPLETED)
    story.expect_worker(worker, state=WorkerState.MERGED)
    story.expect_stack(story.agents.subject, Ready)
