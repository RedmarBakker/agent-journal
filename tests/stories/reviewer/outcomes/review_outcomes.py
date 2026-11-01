import pytest

from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.reviewing.states.reviewing import Reviewing
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.reviewer.reviewer_at_work import ReviewerAtWork

pytestmark = pytest.mark.xfail(strict=True, reason="Plan 4 task 152 (R04: Persist execution outcomes, waiting intervals and delivery history).")


@story(ReviewerAtWork, subject=AgentRole.REVIEWER)
def test_a_review_that_passes_every_point_records_signoff_before_merge(story):
    plan = story.user_opens(f"/journal/plans/{story.plans.first}")
    plan.expect_viewer_shows("id", story.plans.first)
    result = story.agent_runs(story.agents.subject, "review record '1 passed. 2 passed.'")
    result.expect_command_passed()
    result.expect_command_text("signed off")
    result = story.user_opens(f"/journal/tasks/{story.tasks.briefed}/outcomes")
    result.expect_viewer_shows("review_status", "accepted")
    result.expect_viewer_shows("reviewed_worker_id", story.agents.workers.first().number)
    result.expect_viewer_shows("accepted_artifact_completion", True)
    story.expect_task(story.tasks.briefed, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Void, Reviewing, Ended)


@story(ReviewerAtWork, subject=AgentRole.REVIEWER)
def test_a_review_shortfall_stays_in_the_outcome_and_returns_work_for_rework(story):
    task = story.user_opens(f"/journal/tasks/{story.tasks.briefed}")
    task.expect_viewer_shows("id", story.tasks.briefed)
    result = story.agent_runs(story.agents.subject, "review record '1 passed. 2 short: the names of the rules are missing.'")
    result.expect_command_passed()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DISPATCHED)
    result = story.user_opens(f"/journal/tasks/{story.tasks.briefed}/outcomes")
    result.expect_viewer_shows("review_status", "short")
    result.expect_viewer_shows("accepted_artifact_completion", False)
    result.expect_viewer_rows("rework_reasons", "point", [2])
    result.expect_viewer_rows("rework_reasons", "reason", ["the names of the rules are missing"])
    story.expect_stack(story.agents.subject, Void, Reviewing, Ended)


@story(ReviewerAtWork, subject=AgentRole.REVIEWER)
def test_an_undecided_review_keeps_completion_open_for_the_dispatching_agent(story):
    worker = story.user_opens("/journal/workers/activity")
    worker.expect_viewer_passed()
    result = story.agent_runs(story.agents.subject, "review record '1 passed. 2 undecided: inspect the deployment evidence.'")
    result.expect_command_passed()
    result = story.user_opens(f"/journal/tasks/{story.tasks.briefed}/outcomes")
    result.expect_viewer_shows("review_status", "awaiting owner decision")
    result.expect_viewer_shows("accepted_artifact_completion", False)
    result.expect_viewer_shows("accepted_merge_at", None)
    story.expect_stack(story.agents.subject, Void, Reviewing, Ended)


@story(ReviewerAtWork, subject=AgentRole.REVIEWER)
def test_a_reviewer_that_ends_without_a_report_records_a_failed_review_without_completion(story):
    story.agent_ends_the_session(story.agents.subject)
    result = story.user_opens(f"/journal/tasks/{story.tasks.briefed}/outcomes")
    result.expect_viewer_shows("review_status", "failed")
    result.expect_viewer_shows("accepted_artifact_completion", False)
    story.expect_stack(story.agents.subject, Void, Reviewing, Ended)
