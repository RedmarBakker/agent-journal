import pytest

from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.paused_plan import PausedPlan
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 151 (R03: Record builder sizes and estimate revisions).")
def test_estimates_mode_starts_off_and_is_not_promoted_by_new_history(story):
    result = story.user_opens("/journal/settings")
    result.expect_viewer_part(("estimates", "mode"), "off")
    result = story.user_opens("/journal/plans")
    result.expect_viewer_shows("estimates_mode", "off")
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 151 (R03: Record builder sizes and estimate revisions).")
def test_record_and_report_modes_collect_facts_without_new_sizing_refusals(story):
    for mode in ("record", "report"):
        changed = story.user_presses("/journal/settings", {"estimates": {"mode": mode}})
        changed.expect_viewer_passed()
        result = story.user_opens(f"/journal/tasks/{story.tasks.first}")
        result.expect_viewer_shows("size_required_to_start", False)
        result.expect_viewer_shows("estimates_mode", mode)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 161 (W02: Enforce composition readiness and bounded risk advice).")
def test_enforce_mode_is_refused_until_the_owner_sets_valid_positive_ceilings(story):
    result = story.user_presses("/journal/settings", {"estimates": {"mode": "enforce"}})
    result.expect_viewer_refused("positive owner-configured ceilings")
    result = story.user_opens("/journal/settings")
    result.expect_viewer_part(("estimates", "mode"), "off")
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 161 (W02: Enforce composition readiness and bounded risk advice).")
def test_enforce_mode_requires_size_domain_policy_and_a_reviewed_dependency_graph_for_new_work(story):
    changed = story.user_presses("/journal/settings", {"estimates": {"limits": {"queue_wip": 2, "plan_wip": 2, "domain_wip": 2}, "mode": "enforce"}})
    changed.expect_viewer_passed()
    result = story.agent_runs(story.agents.subject, f"task start {story.tasks.first}")
    result.expect_command_refused()
    result.expect_command_text("size, domain, definition of done, and reviewed dependencies")
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_enabling_enforce_does_not_retroactively_strand_an_approved_started_plan(story):
    changed = story.user_presses("/journal/settings", {"estimates": {"limits": {"queue_wip": 2, "plan_wip": 2, "domain_wip": 2}, "mode": "enforce"}})
    changed.expect_viewer_passed()
    result = story.user_opens("/journal/settings")
    result.expect_viewer_part(("estimates", "mode"), "enforce")
    result = story.agent_runs(story.agents.subject, f"task complete {story.tasks.first} --how 'legacy approved work completed'")
    result.expect_command_passed()
    story.expect_task(story.tasks.first, state="completed")
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 155 (D02: Add baseline finish ranges and sprint probability).")
def test_a_forecast_cannot_approve_start_or_dispose_of_a_plan(story):
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("status", "not enough history")
    started = story.user_presses(f"/journal/plans/{story.plans.first}/start", {})
    started.expect_viewer_refused("approved")
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_stack(story.agents.subject, Ready)


@story(PausedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 155 (D02: Add baseline finish ranges and sprint probability).")
def test_a_forecast_does_not_resume_an_owner_paused_plan_or_cross_its_checkpoint(story):
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("status", "not enough history")
    result.expect_viewer_shows("available_actions", [])
    story.expect_plan(story.plans.first, state=PlanState.PAUSED)
    story.expect_task(story.tasks.first, state=TaskState.PAUSED)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 157 (G01: Write planned prerequisites with one cycle check).")
def test_an_intentionally_empty_reviewed_dependency_graph_is_not_treated_as_missing(story):
    reviewed = story.user_presses(f"/journal/plans/{story.plans.first}/dependencies/review", {"edges": [], "intentional": True})
    reviewed.expect_viewer_passed()
    result = story.user_opens(f"/journal/plans/{story.plans.first}/dependencies")
    result.expect_viewer_shows("reviewed", True)
    result.expect_viewer_shows("edges", [])
    story.expect_stack(story.agents.subject, Ready)
