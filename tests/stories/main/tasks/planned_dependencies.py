from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.models.plan_state import PlanState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.main.domain_development_delivered import DomainDevelopmentDelivered
from tests.stories.fixtures.worker.plan_worker import PlanWorker

@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_planned_prerequisite_stays_open_until_its_task_is_accepted(story):
    dependent = story.tasks.second
    prerequisite = story.tasks.first
    result = story.agent_runs(story.agents.subject, f"task depends {dependent} --on {prerequisite} --reason 'the second task uses the first task output'")
    result.expect_command_passed()
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.expect_task(prerequisite, state=TaskState.STARTED)
    story.expect_task(dependent, state=TaskState.OPEN)
    result = story.agent_runs(story.agents.subject, f"task start {dependent}")
    result.expect_command_refused()
    story.agent_runs(story.agents.subject, f"task complete {prerequisite} --how 'accepted artifact'")
    story.expect_task(dependent, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_viewer_cannot_start_a_task_with_an_unaccepted_prerequisite(story):
    story.agent_runs(story.agents.subject, f"task depends {story.tasks.second} --on {story.tasks.first} --reason 'the second task uses the first task output'").expect_command_passed()
    story.user_approves_plan(story.plans.first)
    result = story.user_presses(f"/journal/tasks/{story.tasks.second}/start", {})
    result.expect_viewer_refused("planned prerequisite")
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_cancelled_prerequisite_does_not_release_its_planned_dependent(story):
    dependent, prerequisite = story.tasks.second, story.tasks.first
    story.agent_runs(story.agents.subject, f"task depends {dependent} --on {prerequisite} --reason 'the second task uses the first task output'").expect_command_passed()
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.user_cancels_task(prerequisite, "the prerequisite was withdrawn")
    story.expect_task(dependent, state=TaskState.OPEN)
    result = story.agent_runs(story.agents.subject, f"task start {dependent}")
    result.expect_command_refused()
    revised = story.user_presses(f"/journal/plans/{story.plans.first}/dependencies", {"task_id": dependent, "prerequisites": [], "reason": "the owner removed the cancelled prerequisite"})
    revised.expect_viewer_passed()
    revised.expect_viewer_shows("edges", [])
    story.expect_task_logged(dependent, "the owner removed the cancelled prerequisite")
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_started_task_keeps_its_planned_prerequisites(story):
    dependent, prerequisite = story.tasks.second, story.tasks.first
    story.agent_runs(story.agents.subject, f"task depends {dependent} --on {prerequisite} --reason 'the second task uses the first task output'").expect_command_passed()
    story.user_approves_plan(story.plans.first)
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    result = story.user_presses(f"/journal/plans/{story.plans.first}/dependencies", {
        "task_id": prerequisite, "prerequisites": [dependent], "reason": "the owner tried to revise work already started",
    })
    result.expect_viewer_refused("before it starts")
    edges = story.user_opens(f"/journal/plans/{story.plans.first}/dependencies")
    edges.expect_viewer_rows("edges", "task_id", [dependent])
    edges.expect_viewer_rows("edges", "prerequisite_id", [prerequisite])
    story.expect_task(prerequisite, state=TaskState.STARTED)
    story.expect_task(dependent, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_finished_unmerged_worker_task_is_not_an_accepted_prerequisite(story):
    dependent, prerequisite = story.tasks.second, story.tasks.first
    dependency = story.user_presses(f"/journal/plans/{story.plans.first}/dependencies", {"task_id": dependent, "prerequisites": [prerequisite], "reason": "the second task uses the first task output"})
    dependency.expect_viewer_passed()
    story.user_approves_plan(story.plans.first)
    worker_id = story.agent_dispatches_worker_on_plan(story.agents.subject, "Lady Lovelace", story.plans.first)
    worker = story.agents.workers.get(worker_id)
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


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_cannot_wait_on_its_own_plan(story):
    result = story.agent_runs(story.agents.subject, f"task block {story.tasks.first} --on plan:{story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text("cycle")
    story.expect_task(story.tasks.first, state=TaskState.OPEN, waits=[])
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_one_cycle_check_rejects_a_mixed_planned_dependency_and_runtime_wait_without_partial_write(story):
    dependent, prerequisite = story.tasks.second, story.tasks.first
    story.agent_runs(story.agents.subject, f"task block {dependent} --on task:{prerequisite}").expect_command_passed()
    result = story.agent_runs(story.agents.subject, f"task depends {prerequisite} --on {dependent} --reason 'the tasks depend on each other'")
    result.expect_command_refused()
    result.expect_command_text("cycle")
    edges = story.user_opens(f"/journal/plans/{story.plans.first}/dependencies")
    edges.expect_viewer_shows("edges", [])
    story.expect_task(dependent, state=TaskState.BLOCKED, waits=[f"tasks:{prerequisite}"])
    story.expect_task(prerequisite, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_phase_order_does_not_create_a_planned_dependency_by_itself(story):
    result = story.user_opens(f"/journal/plans/{story.plans.first}/dependencies")
    result.expect_viewer_shows("edges", [])
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_planned_dependency_change_cannot_take_a_task_from_its_worker(story):
    result = story.user_presses(f"/journal/plans/{story.plans.first}/dependencies", {"task_id": story.tasks.first, "prerequisites": [story.tasks.second], "reason": "the owner revised the plan"})
    result.expect_viewer_refused("worker")
    edges = story.user_opens(f"/journal/plans/{story.plans.first}/dependencies")
    edges.expect_viewer_shows("edges", [])
    story.expect_task(story.tasks.first, delegated=True)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_builder_can_set_prerequisites_while_composing_a_task(story):
    other = story.user_creates_plan("parallel work", "work that can run beside the first plan")
    independent = story.user_adds_plan_task(other, "independent work")
    added = story.agent_runs(story.agents.subject, f"plan add {other} 'dependent work' --brief 'use the first plan output' --after {story.tasks.first} --reason 'the task consumes the first plan output'")
    added.expect_command_passed()
    edges = story.user_opens(f"/journal/plans/{other}/dependencies")
    edges.expect_viewer_rows("edges", "prerequisite_id", [story.tasks.first])
    dependent_task = edges.viewer_answer["edges"][0]["task_id"]
    story.user_approves_plan(other)
    story.agent_runs(story.agents.subject, f"plan start {other}")
    story.expect_task(independent, state=TaskState.STARTED)
    story.expect_task(dependent_task, state=TaskState.OPEN)
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_cannot_depend_on_itself(story):
    result = story.agent_runs(story.agents.subject, f"task depends {story.tasks.first} --on {story.tasks.first} --reason 'self reference'")
    result.expect_command_refused()
    result.expect_command_text("cycle")
    edges = story.user_opens(f"/journal/plans/{story.plans.first}/dependencies")
    edges.expect_viewer_shows("edges", [])
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_hidden_prerequisite_is_refused_without_writing_an_edge(story):
    result = story.agent_runs(story.agents.subject, f"task depends {story.tasks.second} --on 999999 --reason 'the task needs a prerequisite'")
    result.expect_command_refused()
    edges = story.user_opens(f"/journal/plans/{story.plans.first}/dependencies")
    edges.expect_viewer_shows("edges", [])
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_agent_that_is_not_the_owner_or_active_plan_builder_cannot_edit_prerequisites(story):
    result = story.agent_runs(story.agents.subject, f"task depends {story.tasks.second} --on {story.tasks.first} --reason 'the task order changed'")
    result.expect_command_refused()
    result.expect_command_text("plan owner or active plan builder")
    edges = story.user_opens(f"/journal/plans/{story.plans.first}/dependencies")
    edges.expect_viewer_shows("edges", [])
    story.expect_stack(story.agents.subject, Ready)


@story(DomainDevelopmentDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_delivery_gate_waits_for_the_existing_accepted_domain_evidence(story):
    added = story.user_presses(f"/journal/plans/{story.plans.first}/tasks", {
        "title": "deploy the committed revision", "brief": "- deployed revision is accepted", "delivery_gate_for": story.tasks.first,
        "reason": "the next handoff requires production deployment",
    })
    added.expect_viewer_passed()
    gate = added.viewer_answer["id"]
    rejected = story.user_presses(f"/journal/tasks/{gate}/finish", {"how": "deployment completed"})
    rejected.expect_viewer_refused("accepted delivery evidence")
    story.agent_runs(story.agents.subject, f"worker check {story.agents.workers.first()} 1 --task {story.tasks.first}").expect_command_passed()
    story.agent_runs(story.agents.subject, f"worker merge {story.agents.workers.first()}").expect_command_passed()
    rejected = story.user_presses(f"/journal/tasks/{gate}/finish", {"how": "deployed"})
    rejected.expect_viewer_refused("accepted delivery evidence")
    accepted = story.user_presses(f"/journal/plans/{story.plans.first}/delivery", {
        "evidence": {"kind": "production_deployment", "source": "deployment-42", "reference": "release-42",
                     "artifact": "revision-42", "environment": "production", "result": "succeeded",
                     "task_ids": [story.tasks.first], "occurred_at": "2026-10-30T10:00:00+00:00"},
    })
    accepted.expect_viewer_passed()
    finished = story.user_presses(f"/journal/tasks/{gate}/finish", {"how": "the accepted deployment is ready for handoff"})
    finished.expect_viewer_passed()
    story.expect_task(gate, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Ready)
