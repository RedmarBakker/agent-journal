from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_owner_reads_frozen_scope_and_unmeasured_availability_for_a_sprint(story):
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-10-26", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    sprint = result.viewer_answer["id"]
    result = story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan_id": story.plans.first})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{sprint}/start", {})
    result.expect_viewer_passed()

    result = story.user_opens(f"/journal/sprints/{sprint}/metrics")
    result.expect_viewer_shows("schema_version", "sprint-metrics-v1")
    result.expect_viewer_part(("sprint", "state"), "active")
    result.expect_viewer_part(("scope", "baseline", "task_ids"), [story.tasks.first, story.tasks.second])
    result.expect_viewer_part(("scope", "baseline", "unknown_size_tasks"), 2)
    result.expect_viewer_part(("scope", "added", "task_count"), 0)
    result.expect_viewer_part(("availability", "status"), "not_measured")
    result.expect_viewer_part(("availability", "daily_observations"), None)
    result.expect_viewer_part(("days", 0, "availability", "actual_places"), None)
    result.expect_viewer_part(("days", 0, "zero_output"), None)
    result.expect_viewer_part(("velocity", "status"), "in_progress")
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)
