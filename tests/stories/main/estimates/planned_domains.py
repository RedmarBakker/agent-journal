import pytest

from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan

pytestmark = pytest.mark.xfail(strict=True, reason="Plan 4 task 150 (R02: Version domain definitions of done and accepted delivery evidence).")


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_plan_composition_records_one_accountable_domain_before_dispatch(story):
    result = story.user_presses(f"/journal/plans/{story.plans.first}/tasks", {"title": "ship the page", "brief": "build and deploy", "size": 3, "domain": "development"})
    result.expect_viewer_passed()
    task = result.viewer_answer["id"]
    result = story.user_opens(f"/journal/tasks/{task}")
    result.expect_viewer_shows("planned_domain", "development")
    result.expect_viewer_shows("size", 3)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_a_task_cannot_claim_two_accountable_domains_and_names_the_split_remedy(story):
    result = story.user_presses(f"/journal/plans/{story.plans.first}/tasks", {"title": "build and publish", "brief": "separate work", "domain": ["development", "publishing"]})
    result.expect_viewer_refused("split")
    story.expect_task_count(2)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_a_later_actual_handoff_does_not_overwrite_the_planned_domain(story):
    result = story.user_presses(f"/journal/tasks/{story.tasks.first}/domain", {"domain": "development", "kind": "planned", "reason": "plan ownership"})
    result.expect_viewer_passed()
    result = story.user_presses(f"/journal/tasks/{story.tasks.first}/domain", {"domain": "operations", "kind": "actual", "reason": "operations accepts deployment"})
    result.expect_viewer_passed()
    result = story.user_opens(f"/journal/tasks/{story.tasks.first}")
    result.expect_viewer_shows("planned_domain", "development")
    result.expect_viewer_shows("actual_domain", "operations")
    result.expect_viewer_shows("credited_domains", ["development"])
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
def test_an_unassigned_domain_or_missing_policy_stays_unknown(story):
    result = story.user_opens(f"/journal/tasks/{story.tasks.first}")
    result.expect_viewer_shows("planned_domain", None)
    result.expect_viewer_shows("delivery_status", "definition of done not set")
    result.expect_viewer_shows("delivery_probability", None)
    story.expect_stack(story.agents.subject, Ready)
