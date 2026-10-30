from datetime import datetime, timezone

from journal.engine.clock import Clock
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.closed_development_sprint import ClosedDevelopmentSprint


@story(ClosedDevelopmentSprint, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_missed_sprint_keeps_its_promise_and_carries_only_the_real_remainder(story):
    period = story.user_opens(f"/journal/sprints/{story.sprints.first}")
    committed_tasks = period.viewer_answer["commitments"][0]["tasks"]
    remaining_criteria = next(row["criteria_version"] for row in committed_tasks if row["id"] == story.tasks.second)
    forecast = story.user_opens(f"/journal/sprints/{story.sprints.first}/forecast")
    forecast.expect_viewer_shows("status", "not enough history")
    close_sprint(story, story.sprints.first, period.viewer_answer["ends_at"])
    story.agent_reads(story.agents.subject).expect_allowed()
    story.user_presses(f"/journal/sprints/{story.sprints.first}/close", {}).expect_viewer_passed()
    closed = story.user_opens(f"/journal/sprints/{story.sprints.first}")
    closed.expect_viewer_rows("changes", "change_type", ["sprint_closed"])
    original = story.user_opens(f"/journal/sprints/{story.sprints.first}/metrics")
    original.expect_viewer_part(("retrospective", "schema_version"), "sprint-retrospective-v1")
    original.expect_viewer_part(("retrospective", "actual", "missed"), True)
    original.expect_viewer_part(("retrospective", "warnings"), ["The sprint closed after its fixed end date; its calendar was not extended."])
    original.expect_viewer_part(("retrospective", "planned", "starts_at"), period.viewer_answer["starts_at"])
    original.expect_viewer_part(("retrospective", "planned", "ends_at"), period.viewer_answer["ends_at"])
    original.expect_viewer_part(("retrospective", "actual", "started_at"), period.viewer_answer["started_at"])
    original.expect_viewer_part_is_truthy(("retrospective", "actual", "closed_at"))
    original.expect_viewer_part(("retrospective", "forecasts", "status"), "not_enough_history")
    original.expect_viewer_part(("retrospective", "forecasts", "snapshots"), [])
    original.expect_viewer_part(("retrospective", "scope_at_close", "originally_committed_task_ids"), [story.tasks.first, story.tasks.second])
    original.expect_viewer_part(("retrospective", "scope_at_close", "added_task_ids"), [])
    original.expect_viewer_part(("retrospective", "scope_at_close", "scope_task_ids"), [story.tasks.first, story.tasks.second])
    original.expect_viewer_part(("retrospective", "scope_at_close", "remaining_task_ids"), [story.tasks.first, story.tasks.second])
    original.expect_viewer_part(("retrospective", "scope_at_close", "delivered_task_ids"), [])
    original.expect_viewer_part(("retrospective", "scope_at_close", "remaining_by_domain", 0, "domain"), "development")
    original.expect_viewer_part(("retrospective", "scope_at_close", "remaining_by_domain", 0, "task_ids"), [story.tasks.first, story.tasks.second])
    original.expect_viewer_part(("retrospective", "cost_availability", "status"), "not_measured")
    original.expect_viewer_part(("retrospective", "range_errors", "status"), "not_enough_history")
    original.expect_viewer_part(("retrospective", "task_outcomes", 0, "measurements", "cost", "label"), "Not measured")

    evidence = story.user_presses(f"/journal/plans/{story.plans.first}/delivery", {"action": "accept", "evidence": {
        "kind": "production_deployment", "source": "deploy-162", "reference": "release-162",
        "task_ids": [story.tasks.first],
        "occurred_at": datetime.fromtimestamp(story.app.container.get(Clock).held_at + 60, timezone.utc).isoformat(),
        "artifact": "revision-162",
        "environment": "production", "result": "succeeded",
    }})
    evidence.expect_viewer_passed()
    added = story.user_presses(f"/journal/plans/{story.plans.first}/tasks", {
        "title": "new scope after the sprint", "brief": "- the new scope is separately planned", "size": 3, "domain": "development",
    })
    added.expect_viewer_passed()
    next_period = story.user_presses("/journal/sprints", {"starts_on": original.viewer_answer["retrospective"]["planned"]["ends_on"], "timezone": "Europe/Amsterdam"})
    next_period.expect_viewer_passed()
    next_sprint = next_period.viewer_answer["id"]
    carried = story.user_presses(f"/journal/sprints/{story.sprints.first}/carry", {
        "plan_id": story.plans.first, "next_sprint_id": next_sprint, "reason": "carry the unfinished task after the deployment was accepted",
    })
    carried.expect_viewer_passed()
    carried.expect_viewer_part(("changes", 1, "data", "tasks", 0, "criteria_version"), remaining_criteria)
    repeated = story.user_presses(f"/journal/sprints/{story.sprints.first}/carry", {
        "plan_id": story.plans.first, "next_sprint_id": next_sprint, "reason": "repeat the carry request",
    })
    repeated.expect_viewer_passed()
    repeated.expect_viewer_rows("changes", "change_type", ["sprint_closed", "plan_carried"])
    story.user_presses(f"/journal/sprints/{next_sprint}/start", {}).expect_viewer_passed()

    current = story.user_opens(f"/journal/sprints/{next_sprint}")
    current.expect_viewer_shows("plan_ids", [story.plans.first])
    current.expect_viewer_part(("commitments", 0, "plan_id"), story.plans.first)
    current.expect_viewer_part(("commitments", 0, "task_ids"), [story.tasks.second])
    current.expect_viewer_part(("commitments", 0, "tasks", 0, "criteria_version"), remaining_criteria)
    delivery = story.user_opens(f"/journal/plans/{story.plans.first}/delivery")
    delivery.expect_viewer_shows("delivered_task_ids", [story.tasks.first])
    delivery.expect_viewer_rows("history", "state", ["accepted"])
    retrospective = story.user_opens(f"/journal/sprints/{story.sprints.first}/metrics")
    retrospective.expect_viewer_part(("retrospective", "scope_at_close", "remaining_task_ids"), [story.tasks.first, story.tasks.second])
    retrospective.expect_viewer_part(("retrospective", "scope_at_close", "scope_task_ids"), [story.tasks.first, story.tasks.second])
    retrospective.expect_viewer_part(("retrospective", "scope_at_close", "added_task_ids"), [])
    retrospective.expect_viewer_part(("retrospective", "scope_at_close", "remaining_by_domain", 0, "task_ids"), [story.tasks.first, story.tasks.second])
    story.expect_plan(story.plans.first, state=PlanState.APPROVED)
    story.expect_task(story.tasks.first, state=TaskState.COMPLETED, size=3)
    story.expect_task(story.tasks.second, state=TaskState.OPEN, size=3)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.MERGED)
    story.expect_stack(story.agents.subject, Ready)


@story(ClosedDevelopmentSprint, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_sprint_owner_can_return_the_remaining_scope_to_backlog(story):
    period = story.user_opens(f"/journal/sprints/{story.sprints.first}")
    close_sprint(story, story.sprints.first, period.viewer_answer["ends_at"])
    refused = story.user_presses(f"/journal/sprints/{story.sprints.first}/carry", {
        "plan_id": story.plans.first, "next_sprint_id": 0,
    })
    refused.expect_viewer_refused("reason")
    story.user_presses(f"/journal/sprints/{story.sprints.first}/carry", {
        "plan_id": story.plans.first, "next_sprint_id": 0, "reason": "return unfinished work to the backlog",
    }).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{story.sprints.first}/carry", {
        "plan_id": story.plans.first, "next_sprint_id": 0, "reason": "repeat the backlog request",
    }).expect_viewer_passed()

    sprint = story.user_opens(f"/journal/sprints/{story.sprints.first}")
    sprint.expect_viewer_shows("state", "closed")
    sprint.expect_viewer_shows("plan_ids", [story.plans.first])
    sprint.expect_viewer_rows("changes", "change_type", ["sprint_closed", "plan_carried"])
    sprint.expect_viewer_part(("changes", 1, "next_sprint_id"), None)
    sprint.expect_viewer_part(("changes", 1, "data", "task_ids"), [story.tasks.first, story.tasks.second])
    story.expect_plan(story.plans.first, state=PlanState.APPROVED)
    story.expect_task(story.tasks.first, state=TaskState.COMPLETED, size=3)
    story.expect_task(story.tasks.second, state=TaskState.OPEN, size=3)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.MERGED)
    story.expect_stack(story.agents.subject, Ready)


def close_sprint(story, sprint_id: int, ends_at: str) -> None:
    end = datetime.fromisoformat(ends_at.replace("Z", "+00:00")).timestamp()
    now = story.app.container.get(Clock).held_at
    story.time_travel(seconds=end - now + 1)
    story.user_presses(f"/journal/sprints/{sprint_id}/close", {}).expect_viewer_passed()
