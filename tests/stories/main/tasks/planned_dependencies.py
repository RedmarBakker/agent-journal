from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.worker.plan_worker import PlanWorker


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_planned_prerequisite_stays_open_until_its_task_is_accepted(story):
    dependent = story.tasks.second
    prerequisite = story.tasks.first
    result = story.agent_runs(story.agents.subject, f"task depends {dependent} --on {prerequisite}")
    result.expect_command_passed()
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.expect_task(prerequisite, state=TaskState.STARTED)
    story.expect_task(dependent, state=TaskState.OPEN)
    result = story.agent_runs(story.agents.subject, f"task start {dependent}")
    result.expect_command_refused()
    story.agent_runs(story.agents.subject, f"task complete {prerequisite} --how 'accepted artifact'")
    story.expect_task(dependent, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_cancelled_prerequisite_does_not_release_its_planned_dependent(story):
    dependent, prerequisite = story.tasks.second, story.tasks.first
    story.agent_runs(story.agents.subject, f"task depends {dependent} --on {prerequisite}").expect_command_passed()
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.user_cancels_task(prerequisite, "the prerequisite was withdrawn")
    story.expect_task(dependent, state=TaskState.OPEN)
    result = story.agent_runs(story.agents.subject, f"task start {dependent}")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_finished_unmerged_worker_task_is_not_an_accepted_prerequisite(story):
    dependent, prerequisite = story.tasks.second, story.tasks.first
    dependency = story.agent_runs(story.agents.subject, f"task depends {dependent} --on {prerequisite}")
    dependency.expect_command_passed()
    worker = story.agent_dispatches_worker_on_plan(story.agents.subject, "Lady Lovelace", story.plans.first)
    story.agent_starts_a_session(worker)
    story.agent_clocks_in(worker)
    story.agent_proves(worker, 1, "first.py:3, the prerequisite is implemented")
    story.agent_clocks_out(worker, "the prerequisite is implemented")
    result = story.agent_runs(story.agents.subject, f"task start {story.tasks.second}")
    result.expect_command_refused()
    story.expect_task(story.tasks.first, delegated=True)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_worker(worker, state=WorkerState.DELIVERED)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_one_cycle_check_rejects_a_mixed_planned_dependency_and_runtime_wait_without_partial_write(story):
    dependent = story.agent_creates_task(story.agents.subject, "waits for the active task")
    story.agent_runs(story.agents.subject, f"task block {dependent} --on task:{story.tasks.started}").expect_command_passed()
    result = story.agent_runs(story.agents.subject, f"task depends {story.tasks.started} --on {dependent}")
    result.expect_command_refused()
    result.expect_command_text("cycle")
    story.expect_task(dependent, state=TaskState.BLOCKED, waits=[f"tasks:{story.tasks.started}"])
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_phase_order_does_not_create_a_planned_dependency_by_itself(story):
    result = story.user_opens(f"/journal/plans/{story.plans.first}/dependencies")
    result.expect_viewer_shows("edges", [])
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_planned_dependency_change_cannot_take_a_task_from_its_worker(story):
    result = story.agent_runs(story.agents.subject, f"task depends {story.tasks.first} --on {story.tasks.second}")
    result.expect_command_refused()
    result.expect_command_text("worker")
    story.expect_task(story.tasks.first, delegated=True)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
