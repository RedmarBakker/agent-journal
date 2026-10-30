from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.reviewing.reviewing_nudges import ReviewingNudges
from journal.features.reviewing.states.reviewing import Reviewing
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import ORCHESTRATOR_MODE
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.reviewer.reviewer_at_work import ReviewerAtWork


@story(ReviewerAtWork, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_a_worker_waits_for_its_review_before_the_work_can_be_merged(story):
    worker = story.agents.workers.first()
    story.agent_runs(story.agents.subject, f"worker check {worker} 1")
    story.agent_runs(story.agents.subject, f"worker check {worker} 2")
    result = story.agent_runs(story.agents.subject, f"worker merge {worker}")
    result.expect_command_refused()
    result.expect_command_text("review")
    story.expect_worker(worker, state=WorkerState.DELIVERED, dispatcher=story.main_session(), review_pending=True)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.reviewer_run_ends_without_a_report(story.agents.reviewers.first())
    story.expect_worker(worker, review_pending=False)
    story.expect_agent_told(story.agents.main, ReviewingNudges.REVIEW_FAILED, n=worker, task=story.tasks.briefed)
    story.expect_stack(story.agents.reviewers.first(), Void, Reviewing, Ended)
    story.expect_stack(story.agents.subject, Orchestrating)


@story(ReviewerAtWork, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_a_worker_keeps_its_task_until_its_review_has_ended(story):
    worker = story.agents.workers.first()
    result = story.agent_runs(story.agents.subject, f"worker release {worker} --drop")
    result.expect_command_refused()
    result.expect_command_text("review")
    story.expect_worker(worker, state=WorkerState.DELIVERED)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.reviewer_run_ends_without_a_report(story.agents.reviewers.first())
    story.expect_agent_told(story.agents.main, ReviewingNudges.REVIEW_FAILED, n=worker, task=story.tasks.briefed)
    story.expect_stack(story.agents.reviewers.first(), Void, Reviewing, Ended)
    story.expect_stack(story.agents.subject, Orchestrating)


@story(ReviewerAtWork, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_a_failed_review_names_its_task_after_the_user_cancels_it(story):
    worker = story.agents.workers.first()
    result = story.user_cancels_task(story.tasks.briefed, "the request was withdrawn")
    result.expect_viewer_passed()
    story.expect_task(story.tasks.briefed, state=TaskState.CANCELLED)
    story.reviewer_run_ends_without_a_report(story.agents.reviewers.first())
    story.expect_agent_told(story.agents.main, ReviewingNudges.REVIEW_FAILED, n=worker, task=story.tasks.briefed)
    story.expect_worker(worker, state=WorkerState.RELEASED)
    story.expect_stack(story.agents.reviewers.first(), Void, Reviewing, Ended)
    story.expect_stack(story.agents.subject, Orchestrating)
