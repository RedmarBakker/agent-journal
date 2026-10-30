import pytest

from journal.features.plans.states.following_plan import FollowingPlan
from journal.engine.clock import Clock
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.testing_task import TestingTask as TaskInTesting
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.worker.plan_worker_delivered import PlanWorkerDelivered
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered

pytestmark = pytest.mark.xfail(strict=True, reason="Plan 4 task 152 (R04: Persist execution outcomes, waiting intervals and delivery history).")


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_closed_for_testing_is_not_recorded_as_successful_completion(story):
    story.agent_runs(story.agents.subject, f"task test {story.tasks.first}")
    story.expect_task(story.tasks.first, state=TaskState.TESTING)
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("execution_complete", False)
    result.expect_viewer_shows("task_outcome", "testing")
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_blocked_or_cancelled_task_never_receives_completed_credit(story):
    blocked = story.agent_creates_task(story.agents.subject, "waiting for a certificate")
    story.agent_runs(story.agents.subject, f"task block {blocked} 'waiting on the certificate'")
    story.expect_task(blocked, state=TaskState.BLOCKED)
    cancelled = story.agent_creates_task(story.agents.subject, "cancelled deployment")
    story.agent_runs(story.agents.subject, f"task cancel {cancelled} --why 'deployment was withdrawn'")
    story.expect_task(cancelled, state=TaskState.CANCELLED)
    result = story.user_opens(f"/journal/tasks/{blocked}/outcomes")
    result.expect_viewer_shows("successful_credit", False)
    result = story.user_opens(f"/journal/tasks/{cancelled}/outcomes")
    result.expect_viewer_shows("successful_credit", False)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_reopening_blocked_work_closes_one_block_interval_without_success_credit(story):
    blocked = story.agent_creates_task(story.agents.subject, "the certificate")
    story.agent_runs(story.agents.subject, f"task block {blocked} 'waiting for the certificate'")
    story.time_travel(seconds=1)
    story.agent_runs(story.agents.subject, f"task unblock {blocked}")
    story.expect_task(blocked, state=TaskState.OPEN)
    result = story.user_opens(f"/journal/tasks/{blocked}/outcomes")
    result.expect_viewer_rows("intervals", "kind", ["block"])
    result.expect_viewer_shows("block_closed_at", True)
    result.expect_viewer_shows("reopened_at", True)
    result.expect_viewer_shows("successful_credit", False)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(TaskInTesting, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_failed_test_and_rework_keep_separate_execution_intervals(story):
    run = story.agent_runs_a_command(story.agents.subject, "sh -c 'seq 1 300; exit 3'")
    story.agent_runs(story.agents.subject, f"output test {run}")
    story.expect_task(story.tasks.started, state=TaskState.PAUSED)
    result = story.user_opens(f"/journal/tasks/{story.tasks.started}/outcomes")
    result.expect_viewer_rows("intervals", "kind", ["execution", "testing", "rework"])
    result.expect_viewer_rows("events", "kind", ["TaskStarted", "TaskClosed", "TaskTestFailed"])
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_resolved_wait_and_a_paused_task_resume_are_different_times(story):
    blocked = story.agent_creates_task(story.agents.subject, "the dependency")
    story.agent_runs(story.agents.subject, f"task pause {story.tasks.started} 'waiting for the dependency' --on task:{blocked}")
    story.agent_runs(story.agents.subject, f"task complete {blocked} --how 'dependency is ready'")
    resolved_at = story.app.container.get(Clock).held_at
    story.expect_task(story.tasks.started, state=TaskState.PAUSED)
    story.time_travel(seconds=1)
    story.agent_runs(story.agents.subject, f"task resume {story.tasks.started}")
    resumed_at = story.app.container.get(Clock).held_at
    result = story.user_opens(f"/journal/tasks/{story.tasks.started}/outcomes")
    result.expect_viewer_rows("events", "kind", ["TaskClosed", "TaskWaitEnded", "TaskStarted"])
    result.expect_viewer_shows("wait_resolved_at", resolved_at)
    result.expect_viewer_shows("resumed_at", resumed_at)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_reopening_blocked_work_keeps_each_attempt_and_duplicate_completion_gets_one_credit(story):
    story.agent_runs(story.agents.subject, f"task block {story.tasks.started} 'waiting on review'")
    story.agent_runs(story.agents.subject, f"task unblock {story.tasks.started}")
    story.agent_runs(story.agents.subject, f"task start {story.tasks.started}")
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.started} --how 'accepted artifact'")
    duplicate = story.agent_runs(story.agents.subject, f"task complete {story.tasks.started} --how 'same completion replayed'")
    duplicate.expect_command_refused()
    result = story.user_opens(f"/journal/tasks/{story.tasks.started}/outcomes")
    result.expect_viewer_shows("execution_generations", 2)
    result.expect_viewer_shows("completed_credit_count", 1)
    result.expect_viewer_rows("intervals", "kind", ["execution", "block", "execution"])
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_proof_sendback_stays_in_outcome_history_without_becoming_a_merge(story):
    worker = story.agents.workers.first()
    result = story.agent_runs(story.agents.subject, f"worker check {worker} 1 --task {story.tasks.first} --short 'the first change is missing'")
    result.expect_command_passed()
    result = story.user_opens(f"/journal/tasks/{story.tasks.first}/outcomes")
    result.expect_viewer_rows("shortfalls", "point", [1])
    result.expect_viewer_rows("shortfalls", "reason", ["the first change is missing"])
    result.expect_viewer_shows("accepted_merge_at", None)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_report_does_not_close_the_task_outcome(story):
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("worker_reported", True)
    result.expect_viewer_shows("accepted_merge_at", None)
    result.expect_viewer_shows("execution_complete", False)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_checking_proofs_and_merging_records_accepted_artifact_completion(story):
    worker = story.agents.workers.first()
    story.agent_runs(story.agents.subject, f"worker check {worker} 1")
    story.agent_runs(story.agents.subject, f"worker check {worker} 2")
    merged = story.agent_runs(story.agents.subject, f"worker merge {worker}")
    merged.expect_command_passed()
    result = story.user_opens(f"/journal/tasks/{story.tasks.briefed}/outcomes")
    result.expect_viewer_shows("accepted_artifact_completion", True)
    result.expect_viewer_shows("accepted_merge_worker_id", worker.number)
    result.expect_viewer_shows("successful_credit_count", 1)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_paused_and_open_work_remains_censored_with_unknown_cost(story):
    story.agent_runs(story.agents.subject, f"task pause {story.tasks.first} 'waiting for owner review' --on task:{story.tasks.second}")
    story.time_travel(minutes=60)
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("unfinished_tasks", [story.tasks.first])
    result.expect_viewer_shows("open_backlog_tasks", [story.tasks.second])
    result.expect_viewer_shows("wait_resolved_at", None)
    result.expect_viewer_shows("censored", True)
    result.expect_viewer_shows("cost", None)
    result.expect_viewer_shows("cost_status", "not measured")
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
