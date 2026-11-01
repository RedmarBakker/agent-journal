from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.domain_delivery_setup import merge_worker, production_record
from tests.stories.fixtures.main.domain_development_delivered import DomainDevelopmentDelivered
from tests.stories.fixtures.main.domain_development_delivery_accepted import DomainDevelopmentDeliveryAccepted
from tests.stories.fixtures.main.domain_published_delivered import DomainPublishedDelivered
from tests.stories.fixtures.main.domain_unknown_plan import DomainUnknownPlan
from tests.stories.fixtures.main.domain_verified_delivered import DomainVerifiedDelivered


@story(DomainDevelopmentDelivered, subject=AgentRole.MAIN)
def test_a_development_task_waits_for_accepted_production_evidence_after_merge_and_replay_credits_once(story):
    plan, task = story.plans.first, story.tasks.first
    delivery = f"/journal/plans/{plan}/delivery"
    result = story.user_opens(delivery)
    result.expect_viewer_shows("status", "awaiting_merge")
    result = story.user_presses(delivery, production_record(task, "release-42", "sha256:revision-42"))
    result.expect_viewer_refused("merge gate")
    merge_worker(story)
    result = story.user_opens(delivery)
    result.expect_viewer_shows("status", "awaiting_deployment")
    result.expect_viewer_part(("delivered_task_ids",), [])
    failed = production_record(task, "release-42", "sha256:revision-42")
    failed["evidence"]["result"] = "failed"
    result = story.user_presses(delivery, failed)
    result.expect_viewer_refused("successful deployment")
    result = story.user_opens(delivery)
    result.expect_viewer_shows("status", "awaiting_deployment")
    result.expect_viewer_count("history", 0)
    wrong = {"action": "accept", "evidence": {"kind": "published_output", "source": "release pipeline", "reference": "release-notes-42", "target": "public release notes", "output": "release notes", "task_ids": [task], "occurred_at": "2026-10-30T10:00:00+00:00"}}
    result = story.user_presses(delivery, wrong)
    result.expect_viewer_refused("does not match development's production deployment requirement")
    accepted = production_record(task, "release-42", "sha256:revision-42")
    result = story.user_presses(delivery, accepted)
    result.expect_viewer_passed()
    result = story.user_opens(delivery)
    result.expect_viewer_shows("status", "delivered")
    result.expect_viewer_rows("history", "state", ["accepted"])
    result.expect_viewer_part(("history", 0, "assurance"), "owner_attested")
    result.expect_viewer_part(("history", 0, "evidence", "source"), "deployment pipeline")
    result.expect_viewer_part(("history", 0, "evidence", "artifact"), "sha256:revision-42")
    result.expect_viewer_part(("history", 0, "evidence", "environment"), "production")
    result.expect_viewer_part(("history", 0, "evidence", "result"), "succeeded")
    result.expect_viewer_part(("history", 0, "evidence", "task_ids"), [task])
    result.expect_viewer_part(("delivered_task_ids",), [task])
    result = story.user_presses(delivery, accepted)
    result.expect_viewer_passed()
    result = story.user_opens(delivery)
    result.expect_viewer_count("history", 1)
    result.expect_viewer_part(("delivered_task_ids",), [task])
    story.expect_stack(story.agents.subject, Ready)


@story(DomainVerifiedDelivered, subject=AgentRole.MAIN)
def test_a_domain_with_verified_output_accepts_a_checked_merge_through_the_same_evidence_origin(story):
    result = story.user_opens(f"/journal/plans/{story.plans.first}/delivery")
    result.expect_viewer_shows("status", "delivered")
    result.expect_viewer_rows("history", "state", ["accepted"])
    result.expect_viewer_part(("history", 0, "evidence", "kind"), "verified_output")
    result.expect_viewer_part(("history", 0, "assurance"), "journal_verified")
    result.expect_viewer_part(("delivered_task_ids",), [story.tasks.first])
    story.expect_stack(story.agents.subject, Ready)


@story(DomainPublishedDelivered, subject=AgentRole.MAIN)
def test_a_published_output_domain_needs_its_configured_evidence_not_a_deployment(story):
    delivery = f"/journal/plans/{story.plans.first}/delivery"
    result = story.user_opens(delivery)
    result.expect_viewer_shows("status", "awaiting_evidence")
    evidence = {"action": "accept", "evidence": {"kind": "published_output", "source": "release pipeline", "reference": "docs/release-42", "target": "public release notes", "output": "release notes", "task_ids": [story.tasks.first], "occurred_at": "2026-10-30T10:00:00+00:00"}}
    result = story.user_presses(delivery, evidence)
    result.expect_viewer_passed()
    result = story.user_opens(delivery)
    result.expect_viewer_shows("status", "delivered")
    result.expect_viewer_part(("history", 0, "evidence", "kind"), "published_output")
    story.expect_stack(story.agents.subject, Ready)


@story(DomainUnknownPlan, subject=AgentRole.MAIN)
def test_a_domain_without_a_done_policy_stays_unknown_and_rejects_delivery_credit(story):
    delivery = f"/journal/plans/{story.plans.first}/delivery"
    result = story.user_opens(delivery)
    result.expect_viewer_shows("status", "unknown")
    result.expect_viewer_part(("tasks", 0, "reason"), "definition of done not set")
    result = story.user_presses(delivery, {"action": "accept", "evidence": {"kind": "published_output", "source": "release pipeline", "reference": "docs/unknown", "target": "unknown", "output": "unknown", "task_ids": [story.tasks.first], "occurred_at": "2026-10-30T10:00:00+00:00"}})
    result.expect_viewer_refused("definition of done not set")
    result = story.user_opens(delivery)
    result.expect_viewer_count("history", 0)
    result.expect_viewer_part(("delivered_task_ids",), [])
    story.expect_stack(story.agents.subject, Ready)


@story(DomainDevelopmentDeliveryAccepted, subject=AgentRole.MAIN)
def test_reopening_delivery_keeps_prior_evidence_and_a_new_generation_earns_credit_once(story):
    delivery = f"/journal/plans/{story.plans.first}/delivery"
    result = story.user_presses(delivery, {"action": "reopen", "task_ids": [story.tasks.first], "reason": "the deployment was rolled back"})
    result.expect_viewer_passed()
    result = story.user_opens(delivery)
    result.expect_viewer_rows("history", "state", ["accepted", "reopened"])
    result.expect_viewer_part(("history", 0, "generation"), 1)
    result.expect_viewer_part(("history", 1, "generation"), 2)
    result.expect_viewer_part(("delivered_task_ids",), [])
    result = story.user_presses(delivery, production_record(story.tasks.first, "release-43", "sha256:revision-43"))
    result.expect_viewer_passed()
    result = story.user_opens(delivery)
    result.expect_viewer_rows("history", "state", ["accepted", "reopened", "accepted"])
    result.expect_viewer_part(("history", 2, "generation"), 2)
    result.expect_viewer_part(("delivered_task_ids",), [story.tasks.first])
    story.expect_stack(story.agents.subject, Ready)
