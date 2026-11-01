from journal.features.tasks.states.ready import Ready
from journal.features.estimates.estimates_options import EstimatesOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.active_sprint_with_draft_plan import ActiveSprintWithDraftPlan
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_sprint_calendar_keeps_local_days_across_daylight_saving(story):
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-03-23", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    sprint = result.viewer_answer["id"]
    result = story.user_opens(f"/journal/sprints/{sprint}")
    result.expect_viewer_shows("starts_on", "2026-03-23")
    result.expect_viewer_shows("ends_on", "2026-04-06")
    result.expect_viewer_shows("length_days", 14)
    result.expect_viewer_shows("timezone", "Europe/Amsterdam")
    result.expect_viewer_shows("starts_at", "2026-03-22T23:00:00+00:00")
    result.expect_viewer_shows("ends_at", "2026-04-05T22:00:00+00:00")
    result.expect_viewer_shows("state", "draft")
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_an_unscheduled_plan_stays_visible_in_the_existing_plan_list(story):
    result = story.user_opens("/journal/sprints")
    result.expect_viewer_list_count(0)
    result = story.user_opens(f"/journal/plans?ids={story.plans.first}")
    result.expect_viewer_rows("rows", "id", [story.plans.first])
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@setting(EstimatesOptions.SPRINT_LENGTH_DAYS, 14)
@story(WorkingAgent, subject=AgentRole.MAIN)
def test_calendar_edits_apply_to_drafts_and_length_changes_only_apply_to_future_periods(story):
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-11-02", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    first_sprint = result.viewer_answer["id"]
    result = story.user_presses(f"/journal/sprints/{first_sprint}/calendar", {"starts_on": "2026-11-03", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    result = story.user_presses("/journal/settings", {"estimates": {"sprint_length_days": 21}})
    result.expect_viewer_passed()
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-11-17", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    next_sprint = result.viewer_answer["id"]
    result = story.user_opens(f"/journal/sprints/{first_sprint}")
    result.expect_viewer_shows("starts_on", "2026-11-03")
    result.expect_viewer_shows("ends_on", "2026-11-17")
    result.expect_viewer_shows("length_days", 14)
    result = story.user_opens(f"/journal/sprints/{next_sprint}")
    result.expect_viewer_shows("ends_on", "2026-12-08")
    result.expect_viewer_shows("length_days", 21)
    result.expect_viewer_shows("calendar_version", 2)
    result = story.user_presses(f"/journal/sprints/{first_sprint}/start", {})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{first_sprint}/calendar", {"starts_on": "2026-11-04", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_refused("active sprint")
    result = story.user_opens(f"/journal/sprints/{first_sprint}")
    result.expect_viewer_shows("starts_on", "2026-11-03")
    story.expect_stack(story.agents.subject, Ready)


@story(ActiveSprintWithDraftPlan, subject=AgentRole.MAIN)
def test_starting_a_sprint_freezes_plan_scope_without_approving_or_starting_it(story):
    sprint = story.sprints.first
    other_plan = story.user_creates_plan("after the sprint started", "new scope")
    story.user_adds_plan_task(other_plan, "new task")
    result = story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan_id": other_plan, "reason": "expanded commitment"})
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}")
    result.expect_viewer_shows("state", "active")
    result.expect_viewer_rows("commitments", "plan_id", [story.plans.first])
    result.expect_viewer_part(("commitments", 0, "task_ids"), [story.tasks.first, story.tasks.second])
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "size"), None)
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "domain"), None)
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "criteria_version"), None)
    result.expect_viewer_part(("commitments", 0, "tasks", 0, "depends_on"), None)
    result.expect_viewer_part(("plan_ids",), [story.plans.first, other_plan])
    result.expect_viewer_part(("changes", 0, "change_type"), "plan_added")
    result.expect_viewer_part(("changes", 0, "reason"), "expanded commitment")
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_carrying_a_plan_to_the_next_sprint_keeps_its_identity_and_old_commitment(story):
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-10-26", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    first_sprint = result.viewer_answer["id"]
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-11-09", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    next_sprint = result.viewer_answer["id"]
    result = story.user_presses(f"/journal/sprints/{first_sprint}/plans", {"plan_id": story.plans.first})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{first_sprint}/start", {})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{first_sprint}/close", {})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{first_sprint}/carry", {"plan_id": story.plans.first, "next_sprint_id": next_sprint, "reason": "unfinished work"})
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{first_sprint}")
    result.expect_viewer_count("changes", 2)
    result.expect_viewer_part(("changes", 0, "change_type"), "sprint_closed")
    result.expect_viewer_part(("changes", 1, "change_type"), "plan_carried")
    result = story.user_opens(f"/journal/sprints/{first_sprint}")
    result.expect_viewer_shows("state", "closed")
    result.expect_viewer_rows("commitments", "plan_id", [story.plans.first])
    result.expect_viewer_part(("commitments", 0, "task_ids"), [story.tasks.first, story.tasks.second])
    result = story.user_opens(f"/journal/sprints/{next_sprint}")
    result.expect_viewer_part(("plan_ids",), [story.plans.first])
    result = story.user_presses(f"/journal/sprints/{first_sprint}/carry", {"plan_id": story.plans.first, "next_sprint_id": next_sprint, "reason": "unfinished work"})
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{next_sprint}")
    result.expect_viewer_part(("plan_ids",), [story.plans.first])
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_overlapping_sprints_and_active_boundary_edits_are_refused_without_changes(story):
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-10-26", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    sprint = result.viewer_answer["id"]
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-10-30", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_refused("overlap")
    result = story.user_presses("/journal/sprints", {"starts_on": "2026-11-09", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    next_sprint = result.viewer_answer["id"]
    result = story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan_id": story.plans.first})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{sprint}/start", {})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{next_sprint}/plans", {"plan_id": story.plans.first})
    result.expect_viewer_refused("current sprint commitment")
    result = story.user_presses(f"/journal/sprints/{sprint}/calendar", {"starts_on": "2026-11-09", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_refused("active sprint")
    result = story.user_opens(f"/journal/sprints/{sprint}")
    result.expect_viewer_shows("starts_on", "2026-10-26")
    result.expect_viewer_shows("state", "active")
    result = story.user_opens("/journal/sprints")
    result.expect_viewer_list_count(2)
    result = story.user_opens(f"/journal/sprints/{next_sprint}")
    result.expect_viewer_part(("plan_ids",), [])
    result.expect_viewer_shows("state", "draft")
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)
