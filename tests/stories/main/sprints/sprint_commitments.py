import pytest

from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.engine.clock import Clock
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 149 (R01: Store fixed-length sprints and plan commitments).")
def test_a_fourteen_calendar_day_sprint_keeps_local_midnight_across_daylight_saving(story):
    created = story.user_presses("/journal/sprints", {"start": "2027-03-21", "timezone": "Europe/Amsterdam"})
    created.expect_viewer_passed()
    sprint = created.viewer_answer["id"]
    result = story.user_opens(f"/journal/sprints/{sprint}")
    result.expect_viewer_shows("timezone", "Europe/Amsterdam")
    result.expect_viewer_shows("start_utc", "2027-03-20T23:00:00Z")
    result.expect_viewer_shows("end_utc", "2027-04-03T22:00:00Z")
    result.expect_viewer_shows("interval", "[start, end)")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 149 (R01: Store fixed-length sprints and plan commitments).")
def test_an_owner_can_edit_a_draft_period_and_the_edit_applies_before_activation(story):
    created = story.user_presses("/journal/sprints", {"start": story.local_moment(0), "timezone": "Europe/Amsterdam"})
    created.expect_viewer_passed()
    sprint = created.viewer_answer["id"]
    result = story.user_presses(f"/journal/sprints/{sprint}/calendar", {"start": "2027-03-21", "timezone": "Europe/Amsterdam"})
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}")
    result.expect_viewer_shows("start_local", "2027-03-21")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 149 (R01: Store fixed-length sprints and plan commitments).")
def test_an_active_period_keeps_its_dates_and_timezone_when_the_owner_changes_future_settings(story):
    created = story.user_presses("/journal/sprints", {"start": "2027-03-21", "timezone": "Europe/Amsterdam"})
    created.expect_viewer_passed()
    sprint = created.viewer_answer["id"]
    started = story.user_presses(f"/journal/sprints/{sprint}/start", {})
    started.expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{sprint}/calendar", {"start": "2027-03-22", "timezone": "UTC"})
    result.expect_viewer_refused("active")
    result = story.user_opens(f"/journal/sprints/{sprint}")
    result.expect_viewer_shows("timezone", "Europe/Amsterdam")
    result.expect_viewer_shows("start_local", "2027-03-21")
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 149 (R01: Store fixed-length sprints and plan commitments).")
def test_starting_a_sprint_freezes_a_draft_plan_without_approving_or_starting_it(story):
    plan = story.user_opens(f"/journal/plans/{story.plans.first}")
    plan.expect_viewer_shows("state", "draft")
    created = story.user_presses("/journal/sprints", {"start": story.local_moment(0), "timezone": "Europe/Amsterdam"})
    created.expect_viewer_passed()
    sprint = created.viewer_answer["id"]
    added = story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan": story.plans.first})
    added.expect_viewer_passed()
    started = story.user_presses(f"/journal/sprints/{sprint}/start", {})
    started.expect_viewer_passed()
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    result = story.user_opens(f"/journal/sprints/{sprint}/commitment")
    result.expect_viewer_shows("plan_ids", [story.plans.first])
    result.expect_viewer_shows("task_ids", [story.tasks.first, story.tasks.second])
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 149 (R01: Store fixed-length sprints and plan commitments).")
def test_scope_additions_and_removals_after_activation_are_audited_deltas(story):
    task = story.user_opens(f"/journal/tasks/{story.tasks.second}")
    task.expect_viewer_shows("state", "open")
    created = story.user_presses("/journal/sprints", {"start": story.local_moment(0), "timezone": "Europe/Amsterdam"})
    created.expect_viewer_passed()
    sprint = created.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan": story.plans.first}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{sprint}/start", {}).expect_viewer_passed()
    added_task = story.user_adds_plan_task(story.plans.first, "added after the commitment")
    removal_at = story.app.container.get(Clock).held_at
    removed = story.agent_runs(story.agents.subject, f"plan remove {story.plans.first} {story.tasks.second} --why 'the owner removed this scope'")
    removed.expect_command_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}/commitment")
    result.expect_viewer_shows("committed_task_ids", [story.tasks.first, story.tasks.second])
    result.expect_viewer_shows("added_task_ids", [added_task])
    result.expect_viewer_shows("removed_task_ids", [story.tasks.second])
    result.expect_viewer_rows("scope_deltas", "actor_type", ["user", "agent"])
    result.expect_viewer_rows("scope_deltas", "reason", ["", "the owner removed this scope"])
    result.expect_viewer_rows("scope_deltas", "recorded_at", [removal_at, removal_at])
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 149 (R01: Store fixed-length sprints and plan commitments).")
def test_a_plan_has_only_one_current_sprint_commitment(story):
    plan = story.user_opens(f"/journal/plans/{story.plans.first}")
    plan.expect_viewer_shows("state", "draft")
    first = story.user_presses("/journal/sprints", {"start": story.local_moment(0), "timezone": "Europe/Amsterdam"})
    first.expect_viewer_passed()
    second = story.user_presses("/journal/sprints", {"start": "2027-04-01", "timezone": "Europe/Amsterdam"})
    second.expect_viewer_passed()
    first_id, second_id = first.viewer_answer["id"], second.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{first_id}/plans", {"plan": story.plans.first}).expect_viewer_passed()
    result = story.user_presses(f"/journal/sprints/{second_id}/plans", {"plan": story.plans.first})
    result.expect_viewer_refused("current sprint")
    result = story.user_opens(f"/journal/plans/{story.plans.first}")
    result.expect_viewer_shows("current_sprint_id", first_id)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 162 (W03: Close sprint outcomes and record owner-controlled carry-over).")
def test_closing_and_carrying_a_plan_keeps_its_identity_and_does_not_duplicate_credit(story):
    first = story.user_presses("/journal/sprints", {"start": story.local_moment(0), "timezone": "Europe/Amsterdam"})
    first.expect_viewer_passed()
    second = story.user_presses("/journal/sprints", {"start": "2027-04-01", "timezone": "Europe/Amsterdam"})
    second.expect_viewer_passed()
    first_id, second_id = first.viewer_answer["id"], second.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{first_id}/plans", {"plan": story.plans.first}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{first_id}/start", {}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{first_id}/close", {}).expect_viewer_passed()
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    carried = story.user_presses(f"/journal/sprints/{first_id}/carry", {"plan": story.plans.first, "to": second_id})
    carried.expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{first_id}/carry", {"plan": story.plans.first, "to": second_id}).expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{second_id}/commitment")
    result.expect_viewer_shows("plan_ids", [story.plans.first])
    result.expect_viewer_shows("task_ids", [story.tasks.first, story.tasks.second])
    result.expect_viewer_shows("duplicate_memberships", 0)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 155 (D02: Add baseline finish ranges and sprint probability).")
def test_a_sprint_without_a_following_period_does_not_invent_one(story):
    created = story.user_presses("/journal/sprints", {"start": story.local_moment(0), "timezone": "Europe/Amsterdam"})
    created.expect_viewer_passed()
    sprint = created.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{sprint}/start", {}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{sprint}/close", {}).expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}/forecast")
    result.expect_viewer_shows("next_status", "next cycle not scheduled")
    result.expect_viewer_shows("next_end", None)
    story.expect_stack(story.agents.subject, Ready)
