from datetime import datetime

import pytest

from journal.engine.clock import Clock
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.worker.plan_worker_delivered import PlanWorkerDelivered
from tests.stories.fixtures.main.publishing_domain_plan import PublishingDomainPlan


def check_plan_worker_proofs(story):
    worker = story.agents.workers.first()
    story.agent_runs(story.agents.subject, f"worker check {worker} 1 --task {story.tasks.first}")
    story.agent_runs(story.agents.subject, f"worker check {worker} 1 --task {story.tasks.second}")


@story(PlanWorkerDelivered, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 150 (R02: Version domain definitions of done and accepted delivery evidence).")
def test_a_plan_merged_before_sprint_end_is_awaiting_delivery_until_production_evidence_arrives(story):
    created = story.user_presses("/journal/sprints", {"start": story.local_moment(0), "timezone": "Europe/Amsterdam"})
    created.expect_viewer_passed()
    sprint = created.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan": story.plans.first}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{sprint}/start", {}).expect_viewer_passed()
    period = story.user_opens(f"/journal/sprints/{sprint}")
    end = datetime.fromisoformat(period.viewer_answer["end_utc"].replace("Z", "+00:00")).timestamp()
    now = story.app.container.get(Clock).held_at
    story.time_travel(seconds=end - now - 1)
    check_plan_worker_proofs(story)
    merged = story.agent_runs(story.agents.subject, f"worker merge {story.agents.workers.first()}")
    merged.expect_command_passed()
    story.time_travel(seconds=2)
    story.user_presses(f"/journal/sprints/{sprint}/close", {}).expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}/forecast")
    result.expect_viewer_shows("delivery_status", "awaiting deployment")
    result.expect_viewer_shows("delivered_scope", [])
    evidence = story.user_presses(f"/journal/plans/{story.plans.first}/delivery", {"kind": "production_deployment", "source": "deployment-42", "artifact": "revision-42", "environment": "production", "scope": [story.tasks.first, story.tasks.second], "at": story.local_moment(0), "succeeded": True})
    evidence.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}/forecast")
    result.expect_viewer_shows("delivery_status", "delivered after sprint end")
    result.expect_viewer_shows("delivered_scope", [story.tasks.first, story.tasks.second])
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorkerDelivered, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 150 (R02: Version domain definitions of done and accepted delivery evidence).")
def test_a_deployment_at_the_exclusive_sprint_end_is_recorded_after_that_sprint(story):
    plan = story.user_opens(f"/journal/plans/{story.plans.first}")
    plan.expect_viewer_shows("id", story.plans.first)
    created = story.user_presses("/journal/sprints", {"start": "2027-03-21", "timezone": "Europe/Amsterdam"})
    created.expect_viewer_passed()
    sprint = created.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan": story.plans.first}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{sprint}/start", {}).expect_viewer_passed()
    period = story.user_opens(f"/journal/sprints/{sprint}")
    end = datetime.fromisoformat(period.viewer_answer["end_utc"].replace("Z", "+00:00")).timestamp()
    now = story.app.container.get(Clock).held_at
    story.time_travel(seconds=end - now - 1)
    check_plan_worker_proofs(story)
    story.agent_runs(story.agents.subject, f"worker merge {story.agents.workers.first()}").expect_command_passed()
    story.time_travel(seconds=1)
    closed = story.user_presses(f"/journal/sprints/{sprint}/close", {})
    closed.expect_viewer_passed()
    closed.expect_viewer_rows("scope_at_close", "status", ["remaining", "remaining"])
    evidence = story.user_presses(f"/journal/plans/{story.plans.first}/delivery", {"kind": "production_deployment", "source": "deployment-at-boundary", "artifact": "revision-at-boundary", "environment": "production", "scope": [story.tasks.first, story.tasks.second], "at": period.viewer_answer["end_utc"], "succeeded": True})
    evidence.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}/forecast")
    result.expect_viewer_shows("delivery_status", "delivered after sprint end")
    result.expect_viewer_shows("delivered_in_sprint", [])
    result.expect_viewer_shows("delivered_after_sprint", [story.tasks.first, story.tasks.second])
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorkerDelivered, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 150 (R02: Version domain definitions of done and accepted delivery evidence).")
def test_a_worker_report_and_accepted_merge_do_not_stand_in_for_deployment(story):
    check_plan_worker_proofs(story)
    result = story.agent_runs(story.agents.subject, f"worker merge {story.agents.workers.first()}")
    result.expect_command_passed()
    forecast = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    forecast.expect_viewer_shows("execution_complete", True)
    forecast.expect_viewer_shows("delivery_complete", False)
    forecast.expect_viewer_shows("delivery_status", "awaiting deployment")
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 150 (R02: Version domain definitions of done and accepted delivery evidence).")
def test_pending_or_failed_deployment_evidence_earns_no_delivery_credit(story):
    plan = story.user_opens(f"/journal/plans/{story.plans.first}")
    plan.expect_viewer_shows("id", story.plans.first)
    pending = story.user_presses(f"/journal/plans/{story.plans.first}/delivery", {"kind": "production_deployment", "source": "release-9", "artifact": "revision-9", "environment": "production", "scope": [story.tasks.first], "succeeded": False})
    pending.expect_viewer_passed()
    forecast = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    forecast.expect_viewer_shows("delivery_complete", False)
    forecast.expect_viewer_shows("delivered_scope", [])
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 150 (R02: Version domain definitions of done and accepted delivery evidence).")
def test_owner_attested_evidence_is_labelled_and_missing_domain_policy_stays_unknown(story):
    evidence = story.user_presses(f"/journal/plans/{story.plans.first}/delivery", {"kind": "owner_attestation", "source": "release-review", "artifact": "edition-9", "environment": "published", "scope": [story.tasks.first], "assurance": "owner-attested", "accepted": True})
    evidence.expect_viewer_refused("definition of done not set")
    forecast = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    forecast.expect_viewer_shows("delivery_status", "definition of done not set")
    forecast.expect_viewer_shows("delivery_complete", False)
    story.expect_stack(story.agents.subject, Ready)


@story(PublishingDomainPlan, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 150 (R02: Version domain definitions of done and accepted delivery evidence).")
def test_owner_attested_evidence_satisfies_the_policy_of_a_non_development_domain(story):
    assigned = story.user_presses(f"/journal/tasks/{story.tasks.first}/domain", {"domain": "publishing", "kind": "planned", "reason": "the edition's accountable domain"})
    assigned.expect_viewer_passed()
    evidence = story.user_presses(f"/journal/plans/{story.plans.first}/delivery", {"kind": "owner_attestation", "source": "editorial-release", "artifact": "edition-42", "environment": "published", "scope": [story.tasks.first], "assurance": "owner-attested", "succeeded": True})
    evidence.expect_viewer_passed()
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("delivery_complete", True)
    result.expect_viewer_shows("assurance", "owner-attested")
    result.expect_viewer_shows("definition_of_done_version", "publishing-v1")
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 150 (R02: Version domain definitions of done and accepted delivery evidence).")
def test_replaying_the_same_accepted_evidence_does_not_credit_the_scope_twice(story):
    evidence = {"kind": "production_deployment", "source": "deploy-10", "artifact": "revision-10", "environment": "production", "scope": [story.tasks.first], "succeeded": True, "idempotency": "deploy-10"}
    story.user_presses(f"/journal/plans/{story.plans.first}/delivery", evidence).expect_viewer_passed()
    story.user_presses(f"/journal/plans/{story.plans.first}/delivery", evidence).expect_viewer_passed()
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("accepted_delivery_count", 1)
    result.expect_viewer_shows("delivered_scope", [story.tasks.first])
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 152 (R04: Persist execution outcomes, waiting intervals and delivery history).")
def test_rollback_retains_the_old_delivery_and_reopens_one_new_work_generation(story):
    plan = story.user_opens(f"/journal/plans/{story.plans.first}")
    plan.expect_viewer_shows("id", story.plans.first)
    accepted = story.user_presses(f"/journal/plans/{story.plans.first}/delivery", {"kind": "production_deployment", "source": "deploy-11", "artifact": "revision-11", "environment": "production", "scope": [story.tasks.first], "succeeded": True, "idempotency": "deploy-11"})
    accepted.expect_viewer_passed()
    rollback = story.user_presses(f"/journal/plans/{story.plans.first}/delivery", {"kind": "rollback", "source": "rollback-11", "artifact": "revision-11", "environment": "production", "scope": [story.tasks.first], "at": story.local_moment(0)})
    rollback.expect_viewer_passed()
    result = story.user_opens(f"/journal/plans/{story.plans.first}/forecast")
    result.expect_viewer_shows("delivery_generations", 2)
    result.expect_viewer_shows("prior_delivery_retained", True)
    result.expect_viewer_shows("current_delivery_complete", False)
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, subject=AgentRole.MAIN)
@pytest.mark.xfail(strict=True, reason="Plan 4 task 150 (R02: Version domain definitions of done and accepted delivery evidence).")
def test_a_domain_policy_change_does_not_rewrite_the_current_commitment(story):
    created = story.user_presses("/journal/sprints", {"start": story.local_moment(0), "timezone": "Europe/Amsterdam"})
    created.expect_viewer_passed()
    sprint = created.viewer_answer["id"]
    story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan": story.plans.first}).expect_viewer_passed()
    story.user_presses(f"/journal/sprints/{sprint}/start", {}).expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}/commitment")
    original = result.viewer_answer["criteria_version"]
    revised = story.user_presses(f"/journal/sprints/{sprint}/criteria", {"criteria_version": "development-v2", "reason": "owner approved current scope"})
    revised.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}/commitment")
    result.expect_viewer_shows("original_criteria_version", original)
    result.expect_viewer_shows("current_criteria_version", "development-v2")
    result.expect_viewer_shows("criteria_changed_for_commitment", True)
    revised = story.user_presses(f"/journal/sprints/{sprint}/criteria", {"criteria_version": "development-v3", "reason": "criteria revision repeated"})
    revised.expect_viewer_passed()
    result = story.user_opens(f"/journal/sprints/{sprint}/commitment")
    result.expect_viewer_shows("original_criteria_version", original)
    result.expect_viewer_shows("criteria_delta_reason", "criteria revision repeated")
    story.expect_stack(story.agents.subject, Ready)
