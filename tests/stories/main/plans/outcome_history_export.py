from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.domain_development_delivered import DomainDevelopmentDelivered


@setting(EstimatesOptions.MODE, "record")
@story(DomainDevelopmentDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_owner_reads_and_exports_one_scoped_auditable_plan_history(story):
    plan, task = story.plans.first, story.tasks.first
    result = story.user_presses(f"/journal/tasks/{task}/size", {"size": 5, "reason": "the owner sized the committed scope"})
    result.expect_viewer_passed()
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-10-26", "timezone": "UTC"})
    result.expect_viewer_passed()
    sprint = result.viewer_answer["id"]
    result = story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan_id": plan})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{sprint}/start", {})
    result.expect_viewer_passed()
    worker = story.agents.workers.first()
    result = story.agent_runs(story.agents.subject, f"worker check {worker} 1")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, f"worker merge {worker}")
    result.expect_command_passed()
    evidence = {"action": "accept", "evidence": {"kind": "production_deployment", "source": "deployment pipeline", "reference": "release-52",
                "artifact": "sha256:revision-52", "environment": "production", "result": "succeeded", "task_ids": [task],
                "occurred_at": "2026-10-30T10:00:00+00:00"}}
    result = story.user_presses(f"/journal/plans/{plan}/delivery", evidence)
    result.expect_viewer_passed()

    result = story.user_opens(f"/journal/plans/{plan}/outcomes")
    result.expect_viewer_passed()
    result.expect_viewer_shows("schema_version", "plan-outcome-history-v1")
    result.expect_viewer_part(("scope", "plan_mode"), "solo")
    result.expect_viewer_shows("estimates_mode", "record")
    result.expect_viewer_part(("availability", "status"), "not_measured")
    result.expect_viewer_rows("sprints", "id", [sprint])
    result.expect_viewer_part(("sprints", 0, "commitments", 0, "snapshot", "tasks", 0, "size"), 5)
    result.expect_viewer_part(("sprints", 0, "commitments", 0, "actor"), "user:1")
    result.expect_viewer_part(("tasks", 0, "estimate_history", "history", 1, "size"), 5)
    result.expect_viewer_part(("tasks", 0, "estimate_history", "history", 1, "actor"), "user:1")
    result.expect_viewer_part_is_truthy(("tasks", 0, "estimate_history", "history", 1, "recorded_at"))
    result.expect_viewer_part(("tasks", 0, "current_in_plan"), True)
    result.expect_viewer_part(("tasks", 0, "execution", "delivery_accepted"), True)
    result.expect_viewer_part(("tasks", 0, "delivery", "status"), "delivered")
    result.expect_viewer_part(("tasks", 0, "outcomes", 0, "cohort_version"), "plan4-outcome-cohort-v1")
    result.expect_viewer_part_is_truthy(("tasks", 0, "outcomes", 0, "cohort_key"))
    result.expect_viewer_part_is_truthy(("tasks", 0, "outcomes", 0, "recorded_at"))
    result.expect_viewer_part(("delivery", "history", 0, "actor"), "user:1")
    result.expect_viewer_part_is_truthy(("delivery", "history", 0, "created_at"))
    exported = story.user_downloads(f"/journal/plans/{plan}/outcomes/export")
    exported.expect_viewer_downloads_json_equal(result.viewer_answer)

    other_plan = story.user_creates_plan("organization history", "read-only plan history")
    result = story.user_presses(f"/journal/plans/{other_plan}/mode", {"mode": "organization"})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/plans/{other_plan}/tasks", {"title": "not started", "brief": "- preserve missing measurements", "domain": "development"})
    result.expect_viewer_passed()
    other_task = result.viewer_answer["id"]
    result = story.user_opens(f"/journal/plans/{other_plan}/outcomes")
    result.expect_viewer_passed()
    result.expect_viewer_part(("scope", "plan_mode"), "organization")
    result.expect_viewer_part(("tasks", 0, "execution", "active_seconds"), None)
    result.expect_viewer_part(("tasks", 0, "measurements", "active_time", "status"), "not_measured")
    result.expect_viewer_part(("tasks", 0, "measurements", "block_and_wait_time", "seconds"), None)
    result.expect_viewer_part(("tasks", 0, "measurements", "cost", "status"), "not_measured")
    result.expect_viewer_part(("tasks", 0, "measurements", "cost", "amount_dollars"), None)
    result.expect_viewer_part(("tasks", 0, "measurements", "delivery", "status"), "not_evidenced")
    result.expect_viewer_part(("tasks", 0, "data_quality", "status"), "incomplete")

    other_environment = story.another_environment("other")
    other_plans = story.user_opens_in(other_environment, "/journal/plans")
    other_plans.expect_viewer_passed()
    other_plans.expect_viewer_rows("rows", "id", [])
    result = story.user_opens_in(other_environment, f"/journal/plans/{plan}/outcomes")
    result.expect_viewer_not_found_without("release-52")
    result = story.user_sets(EstimatesOptions.MODE, "off")
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/plans/{plan}/outcomes")
    result.expect_viewer_passed()
    result.expect_viewer_shows("estimates_mode", "off")
    result.expect_viewer_part(("delivery", "history", 0, "state"), "accepted")
    story.expect_task(task, state=TaskState.COMPLETED)
    story.expect_task(other_task, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)
