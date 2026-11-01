import pytest

from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.states.external_wait import ExternalWait
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.worker.working_worker import WorkingWorker

pytestmark = pytest.mark.xfail(strict=True, reason="Plan 4 task 151 (R03: Record builder sizes and estimate revisions).")


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_an_owner_can_set_a_story_size_on_an_open_plan_task(story):
    result = story.user_presses(f"/journal/tasks/{story.tasks.first}/size", {"size": 3, "reason": "a reviewed relative estimate"})
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/tasks/{story.tasks.first}")
    result.expect_viewer_shows("size", 3)
    result.expect_viewer_shows("size_unit", "story points")
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_null_is_unknown_and_zero_or_off_scale_story_sizes_are_refused(story):
    result = story.user_opens(f"/journal/tasks/{story.tasks.first}")
    result.expect_viewer_shows("size", None)
    for size in (0, 4, 14):
        refused = story.user_presses(f"/journal/tasks/{story.tasks.first}/size", {"size": size, "reason": "invalid estimate"})
        refused.expect_viewer_refused("story points")
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_an_authorized_resize_keeps_first_ready_and_sprint_commitment_sizes(story):
    result = story.user_presses(f"/journal/tasks/{story.tasks.first}/size", {"size": 3, "reason": "first ready estimate"})
    result.expect_viewer_passed()
    created = story.user_presses("/journal/sprints", {"start": story.local_moment(0), "timezone": "Europe/Amsterdam"})
    created.expect_viewer_passed()
    sprint = created.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan": story.plans.first}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{sprint}/start", {}).expect_viewer_passed()
    changed = story.user_presses(f"/journal/tasks/{story.tasks.first}/size", {"size": 5, "reason": "scope was reviewed"})
    changed.expect_viewer_passed()
    result = story.user_opens(f"/journal/tasks/{story.tasks.first}")
    result.expect_viewer_shows("first_ready_size", 3)
    result.expect_viewer_shows("committed_size", 3)
    result.expect_viewer_shows("current_size", 5)
    result.expect_viewer_shows("resize_reason", "scope was reviewed")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_a_worker_can_propose_a_resize_without_changing_the_accepted_size(story):
    result = story.agent_runs(story.agents.workers.first(), f"task size {story.tasks.briefed} 5 --why 'the work is larger'")
    result.expect_command_passed()
    result.expect_command_text("proposal")
    story.expect_task(story.tasks.briefed, size=None)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(StartedTask, subject=AgentRole.MAIN)
def test_partial_execution_does_not_reduce_the_accepted_story_size(story):
    result = story.user_presses(f"/journal/tasks/{story.tasks.started}/size", {"size": 5, "reason": "planned scope"})
    result.expect_viewer_passed()
    story.agent_runs(story.agents.subject, f"task log {story.tasks.started} 'half the work is done'")
    result = story.user_opens(f"/journal/tasks/{story.tasks.started}")
    result.expect_viewer_shows("size", 5)
    story.expect_task(story.tasks.started, size=5)
    story.expect_stack(story.agents.subject, Ready, Working)
