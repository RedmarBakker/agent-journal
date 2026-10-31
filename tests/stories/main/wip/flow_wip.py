from journal.features.estimates.estimates_nudges import EstimatesNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.closed_development_sprint import ClosedDevelopmentSprint
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.testing_task import TestingTask as TaskInTesting
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.worker.plan_worker_delivered import PlanWorkerDelivered
from tests.stories.fixtures.worker.plan_worker import PlanWorker


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
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_merging_releases_execution_wip_but_awaiting_deployment_stays_in_delivery_wip(story):
    worker = story.agents.workers.first()
    story.agent_runs(story.agents.subject, f"worker check {worker} 1 --task {story.tasks.first}").expect_command_passed()
    story.agent_runs(story.agents.subject, f"worker check {worker} 1 --task {story.tasks.second}").expect_command_passed()
    story.agent_runs(story.agents.subject, f"worker merge {worker}").expect_command_passed()
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("execution_wip_task_ids", [])
    result.expect_viewer_shows("delivery_wip_task_ids", [story.tasks.first])
    result.expect_viewer_shows("wip_total", None)
    story.expect_task(story.tasks.second, state=TaskState.COMPLETED)
    story.expect_worker(worker, state=WorkerState.MERGED)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_waiting_worker_occupies_a_seat_separately_from_plan_flow_wip(story):
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("execution_wip_task_ids", [story.tasks.first])
    result.expect_viewer_shows("occupied_execution_seats", 1)
    result.expect_viewer_shows("delivery_wip_task_ids", [story.tasks.first])
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_wip_ceiling_keeps_a_busy_worker_and_blocks_only_an_extra_start(story):
    worker = story.agents.workers.first()
    changed = story.user_presses("/journal/settings", {"estimates": {"mode": "enforce", "execution_wip": 1}})
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
    changed = story.user_presses("/journal/settings", {"estimates": {"mode": "enforce", "execution_wip": 1}})
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
def test_a_project_execution_ceiling_counts_work_from_other_environments(story):
    other = story.another_environment("other")
    plan_id = story.user_creates_plan_in(other, "other environment plan")
    added = story.user_presses_in(other, f"/journal/plans/{plan_id}/tasks", {
        "title": "other environment work", "brief": "- the other environment task is done",
    })
    added.expect_viewer_passed()
    candidate = added.viewer_answer["id"]
    story.user_presses_in(other, f"/journal/plans/{plan_id}/approve", {}).expect_viewer_passed()
    changed = story.user_presses("/journal/settings", {"estimates": {"mode": "enforce", "execution_wip": 1}})
    changed.expect_viewer_passed()
    story.session_starts_in(other, "s-wip-other")
    plan = story.user_opens_in(other, f"/journal/plans/{plan_id}")
    plan.expect_viewer_shows("state", PlanState.APPROVED.value)

    result = story.agent_in_runs(story.agents.subject, other, "s-wip-other", f"task start {candidate}")

    result.expect_command_refused()
    result.expect_command_text("project execution WIP limit 1 is full")
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_task_in(other, candidate, TaskState.OPEN.value)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_execution_and_delivery_wip_overlap_without_being_added_together(story):
    story.agent_runs(story.agents.subject, f"task block {story.tasks.started} 'waiting on deployment'")
    result = story.user_opens(f"/journal/tasks/{story.tasks.started}/wip")
    result.expect_viewer_shows("execution_wip", True)
    result.expect_viewer_shows("delivery_wip", True)
    result.expect_viewer_shows("combined_wip", None)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_report_mode_shows_flow_limits_without_refusing_new_work(story):
    first = story.tasks.started
    second = story.agent_creates_task(story.agents.subject, "work beyond the report-only limit")
    changed = story.user_presses("/journal/settings", {"estimates": {"mode": "report", "execution_wip": 1}})
    changed.expect_viewer_passed()
    result = story.agent_runs(story.agents.subject, f"task start {second}")
    result.expect_command_passed()
    story.expect_task(first, state=TaskState.BLOCKED)
    story.expect_task(second, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(ClosedDevelopmentSprint, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_unaccepted_delivery_fills_its_plan_limit_until_the_owner_accepts_it(story):
    changed = story.user_presses("/journal/settings", {
        "estimates": {"mode": "enforce", "delivery_wip_per_plan": 1, "delivery_wip_per_domain": 3},
    })
    changed.expect_viewer_passed()
    result = story.agent_runs(story.agents.subject, f"task start {story.tasks.second}")
    result.expect_command_refused()
    result.expect_command_text("plan delivery WIP limit")
    result.expect_command_text("accept the pending domain delivery")
    start = story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    start.expect_command_refused()
    start.expect_command_text("plan delivery WIP limit")
    story.expect_plan(story.plans.first, state=PlanState.APPROVED)
    story.expect_task(story.tasks.first, state=TaskState.COMPLETED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.MERGED)
    story.user_opens(f"/journal/sprints/{story.sprints.first}").expect_viewer_passed()
    story.expect_stack(story.agents.subject, Ready)


@story(ClosedDevelopmentSprint, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_owner_cannot_start_a_plan_past_its_delivery_limit(story):
    changed = story.user_presses("/journal/settings", {
        "estimates": {"mode": "enforce", "delivery_wip_per_plan": 1},
    })
    changed.expect_viewer_passed()

    result = story.user_presses(f"/journal/plans/{story.plans.first}/start", {})

    result.expect_viewer_refused("plan delivery WIP limit")
    story.expect_plan(story.plans.first, state=PlanState.APPROVED)
    story.expect_task(story.tasks.first, state=TaskState.COMPLETED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.MERGED)
    story.user_opens(f"/journal/sprints/{story.sprints.first}").expect_viewer_passed()
    story.expect_stack(story.agents.subject, Ready)


@story(ClosedDevelopmentSprint, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_domain_delivery_limit_applies_across_plans(story):
    other = story.another_environment("other")
    next_plan = story.user_creates_plan_in(other, "another development plan")
    added = story.user_presses_in(other, f"/journal/plans/{next_plan}/tasks", {
        "title": "another release", "brief": "- another release is deployed", "size": 3, "domain": "development",
    })
    added.expect_viewer_passed()
    next_task = added.viewer_answer["id"]
    story.user_presses_in(other, f"/journal/plans/{next_plan}/approve", {}).expect_viewer_passed()
    changed = story.user_presses("/journal/settings", {
        "estimates": {"mode": "enforce", "delivery_wip_per_plan": 2, "delivery_wip_per_domain": 1},
    })
    changed.expect_viewer_passed()
    story.session_starts_in(other, "s-domain-other")

    result = story.agent_in_runs(story.agents.subject, other, "s-domain-other", f"task start {next_task}")
    result.expect_command_refused()
    result.expect_command_text("development delivery WIP limit")
    result.expect_command_text("accept the pending domain delivery")
    plan = story.user_opens_in(other, f"/journal/plans/{next_plan}")
    plan.expect_viewer_shows("state", PlanState.APPROVED.value)
    story.expect_task_in(other, next_task, TaskState.OPEN.value)
    story.expect_plan(story.plans.first, state=PlanState.APPROVED)
    story.expect_task(story.tasks.first, state=TaskState.COMPLETED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.MERGED)
    story.user_opens(f"/journal/sprints/{story.sprints.first}").expect_viewer_passed()
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_cannot_be_assigned_more_than_its_configured_queue_limit(story):
    worker = story.agents.workers.first()
    changed = story.user_presses("/journal/settings", {
        "estimates": {"mode": "enforce", "worker_queue": 2},
    })
    changed.expect_viewer_passed()
    extra = story.agent_creates_task(story.agents.subject, "the next worker assignment")

    result = story.agent_runs(story.agents.subject, f"worker queue {worker} {extra}")
    result.expect_command_refused()
    result.expect_command_text("worker assignment WIP limit")
    result.expect_command_text(f"finish or release its current task or drain its queue with worker drain {worker}")
    story.expect_task(story.tasks.first, delegated=True)
    story.expect_task(story.tasks.second, delegated=True)
    story.expect_task(extra, state=TaskState.OPEN, delegated=False)
    story.expect_worker(worker, state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_testing_work_keeps_the_followed_plan_at_its_execution_ceiling(story):
    changed = story.user_presses("/journal/settings", {
        "estimates": {"mode": "enforce", "execution_wip": 1},
    })
    changed.expect_viewer_passed()

    result = story.agent_runs(story.agents.subject, f"task test {story.tasks.first}")

    result.expect_command_passed()
    result.expect_agent_told(
        story.agents.subject,
        EstimatesNudges.WIP_LIMIT,
        reason=f"project execution WIP limit 1 is full: task {story.tasks.first} is testing; finish testing task {story.tasks.first} before starting task {story.tasks.second}",
    )
    story.expect_task(story.tasks.first, state=TaskState.TESTING)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
