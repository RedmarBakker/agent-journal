from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.main.orchestrator_started_plans import OrchestratorStartedPlans
from tests.stories.fixtures.worker.dependency_plan_worker import DependencyPlanWorker


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_skips_unmet_work_and_starts_it_when_its_prerequisite_is_accepted(story):
    dependent, prerequisite = story.tasks.second, story.tasks.first
    revised = story.user_presses(f"/journal/plans/{story.plans.first}/dependencies", {
        "task_id": dependent, "prerequisites": [prerequisite], "reason": "the second task uses the first task output",
    })
    revised.expect_viewer_passed()
    added = story.user_presses(f"/journal/plans/{story.plans.first}/tasks", {
        "title": "independent work", "brief": "work that does not use the first task",
    })
    added.expect_viewer_passed()
    independent = added.viewer_answer["id"]
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    refused = story.agent_runs(story.agents.subject, f"task start {dependent}")
    refused.expect_command_refused()
    refused.expect_command_text(f"task {prerequisite}")
    story.expect_task(prerequisite, state=TaskState.STARTED)
    story.agent_runs(story.agents.subject, f"task complete {prerequisite} --how 'the accepted artifact is ready'")
    story.expect_task(dependent, state=TaskState.STARTED)
    story.expect_task(independent, state=TaskState.OPEN)
    story.user_cancels_task(prerequisite, "the accepted task was withdrawn after work began")
    story.agent_runs(story.agents.subject, f"task block {dependent} 'set it aside briefly'")
    story.agent_runs(story.agents.subject, f"task unblock {dependent}")
    story.agent_runs(story.agents.subject, f"task start {dependent}")
    story.expect_task(dependent, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_cannot_be_dispatched_directly_on_a_dependent_task(story):
    dependent, prerequisite = story.tasks.second, story.tasks.first
    story.user_presses(f"/journal/plans/{story.plans.first}/dependencies", {
        "task_id": dependent, "prerequisites": [prerequisite], "reason": "the second task uses the first task output",
    }).expect_viewer_passed()
    story.user_approves_plan(story.plans.first)
    refused = story.agent_runs(story.agents.subject, f"worker dispatch 'Lady Lovelace' --task {dependent} --changes 'the dependent task' --profile journal-medior --model sonnet --tests 'Scoped tests'")
    refused.expect_command_refused()
    refused.expect_command_text(f"task {prerequisite}")
    story.expect_task(dependent, state=TaskState.OPEN, delegated=False)
    story.expect_task(prerequisite, state=TaskState.OPEN, delegated=False)
    story.expect_stack(story.agents.subject, Ready)


@story(DependencyPlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_queue_does_not_take_an_unready_planned_dependent(story):
    worker = story.agents.workers.first()
    refused = story.agent_runs(story.agents.subject, f"worker queue {worker} {story.tasks.second}")
    refused.expect_command_refused()
    refused.expect_command_text(f"task {story.tasks.first}")
    story.expect_task(story.tasks.first, state=TaskState.STARTED, delegated=True)
    story.expect_task(story.tasks.second, state=TaskState.OPEN, delegated=False)
    story.expect_worker(worker, state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(OrchestratorStartedPlans, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_an_orchestrator_dispatches_only_plan_tasks_with_accepted_prerequisites(story):
    dependent, prerequisite = story.tasks.second, story.tasks.first
    changed = story.user_presses(f"/journal/plans/{story.plans.first}/dependencies", {
        "task_id": dependent, "prerequisites": [prerequisite], "reason": "the second task uses the first task output",
    })
    changed.expect_viewer_passed()
    worker_id = story.agent_dispatches_worker_on_plan(story.agents.subject, "Lady Lovelace", story.plans.first)
    worker = story.agents.workers.get(worker_id)
    story.agent_starts_a_session(worker)
    story.agent_clocks_in(worker)
    story.expect_task(prerequisite, state=TaskState.STARTED, delegated=True)
    story.expect_task(dependent, state=TaskState.OPEN, delegated=False)
    story.expect_worker(worker_id, state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Orchestrating, OrchestratingPlan, ExternalWait)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_accepted_prerequisite_does_not_clear_a_runtime_wait(story):
    dependent, prerequisite = story.tasks.second, story.tasks.first
    other = story.agent_creates_task(story.agents.subject, "the external wait")
    revised = story.user_presses(f"/journal/plans/{story.plans.first}/dependencies", {
        "task_id": dependent, "prerequisites": [prerequisite], "reason": "the second task uses the first task output",
    })
    revised.expect_viewer_passed()
    story.agent_runs(story.agents.subject, f"task block {dependent} --on task:{other}")
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.agent_runs(story.agents.subject, f"task complete {prerequisite} --how 'the accepted artifact is ready'")
    story.expect_task(dependent, state=TaskState.BLOCKED, waits=[f"tasks:{other}"])
    story.agent_runs(story.agents.subject, f"task complete {other} --how 'the external wait is over'")
    story.expect_task(dependent, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
