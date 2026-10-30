import pytest

from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.testing_task import TestingTask as TaskInTesting
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.worker.plan_worker_delivered import PlanWorkerDelivered
from tests.stories.fixtures.worker.plan_worker import PlanWorker

pytestmark = pytest.mark.xfail(strict=True, reason="Plan 4 task 160 (W01: Apply shared ready ordering and WIP ceilings).")


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_in_hand_task_counts_as_execution_wip_before_it_occupies_any_other_seat(story):
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("execution_wip_task_ids", [story.tasks.first])
    result.expect_viewer_shows("delivery_wip_task_ids", [story.tasks.first])
    result.expect_viewer_shows("occupied_execution_seats", 0)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(TaskInTesting, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_testing_work_stays_in_execution_wip_until_accepted_artifact_completion(story):
    result = story.user_opens(f"/journal/tasks/{story.tasks.started}/wip")
    result.expect_viewer_shows("execution_wip", True)
    result.expect_viewer_shows("stage", "testing")
    result.expect_viewer_shows("delivery_wip", True)
    story.expect_task(story.tasks.started, state=TaskState.TESTING)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_never_started_blocked_task_is_backlog_not_execution_wip(story):
    story.agent_runs(story.agents.subject, f"task block {story.tasks.first} 'waiting for a credential'")
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("execution_wip_task_ids", [])
    result.expect_viewer_shows("blocked_backlog_task_ids", [story.tasks.first])
    story.expect_task(story.tasks.first, state=TaskState.BLOCKED)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_merging_releases_execution_wip_but_awaiting_deployment_stays_in_delivery_wip(story):
    worker = story.agents.workers.first()
    story.agent_runs(story.agents.subject, f"worker check {worker} 1 --task {story.tasks.first}")
    story.agent_runs(story.agents.subject, f"worker check {worker} 1 --task {story.tasks.second}")
    story.agent_runs(story.agents.subject, f"worker merge {worker}").expect_command_passed()
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("execution_wip_task_ids", [])
    result.expect_viewer_shows("delivery_wip_task_ids", [story.tasks.first, story.tasks.second])
    result.expect_viewer_shows("wip_total", None)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_waiting_worker_occupies_a_seat_separately_from_plan_flow_wip(story):
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("execution_wip_task_ids", [story.tasks.first])
    result.expect_viewer_shows("occupied_execution_seats", 1)
    result.expect_viewer_shows("delivery_wip_task_ids", [story.tasks.first])
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_wip_ceiling_keeps_a_busy_worker_and_blocks_only_an_extra_start(story):
    worker = story.agents.workers.first()
    changed = story.user_presses("/journal/settings", {"estimates": {"limits": {"execution_wip": 1}}})
    changed.expect_viewer_passed()
    next_task = story.agent_creates_task(story.agents.subject, "work beyond the flow limit")
    result = story.agent_runs(story.agents.subject, f"task start {next_task}")
    result.expect_command_refused()
    result.expect_command_text("execution WIP limit")
    story.expect_task(story.tasks.first, delegated=True)
    story.expect_worker(worker, state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_lowering_an_owner_limit_does_not_steal_started_work_and_blocks_only_new_work(story):
    changed = story.user_presses("/journal/settings", {"estimates": {"limits": {"execution_wip": 1}}})
    changed.expect_viewer_passed()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    next_task = story.agent_creates_task(story.agents.subject, "the next task")
    result = story.agent_runs(story.agents.subject, f"task start {next_task}")
    result.expect_command_refused()
    result.expect_command_text("execution WIP limit")
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_task(next_task, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_execution_and_delivery_wip_overlap_without_being_added_together(story):
    story.agent_runs(story.agents.subject, f"task pause {story.tasks.started} 'waiting on deployment'")
    result = story.user_opens(f"/journal/tasks/{story.tasks.started}/wip")
    result.expect_viewer_shows("execution_wip", True)
    result.expect_viewer_shows("delivery_wip", True)
    result.expect_viewer_shows("combined_wip", None)
    story.expect_stack(story.agents.subject, Ready)
