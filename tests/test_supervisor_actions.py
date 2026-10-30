from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest

from journal.config import Config
from journal.db.connection import Connection
from journal.models.entry import Entry
from journal.repositories.environments import Environments
from journal.repositories.entries import Entries
from journal.repositories.links import Links
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.support.actor import Actor
from journal.support.large_reads import LargeReads
from journal.support.masks import Masks
from journal.support.query_times import QueryTimes
from journal.support.secret_values import SecretValues
from journal.support.stage_times import StageTimes
from journal.support.time_source import TimeSource
from journal.features.supervisor.support.admissions import SupervisorAdmissions


TOKEN = "supervisor-credential-for-tests"
NOW = datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc)
MODEL = "test/model"


def supervisor_journal(connection, bus, scope, budget=None, prices=None):
    entries = Entries(connection, bus, scope, TimeSource())
    control_entries = SupervisorEntries(entries)
    clock = [NOW]
    tenant_id, grant_id = "tenant-a", "grant-a"
    credential_hash = sha256(TOKEN.encode()).hexdigest()
    saved_budget = budget or {
        "daily_cost_usd": "1.00",
        "daily_turns": 12,
        "daily_input_tokens": 288000,
        "daily_output_tokens": 96000,
        "input_tokens_per_turn": 24000,
        "output_tokens_per_turn": 8000,
        "max_retries": 2,
    }
    credential = {
        "tenant_id": tenant_id,
        "grant_id": grant_id,
        "credential_hash": credential_hash,
        "active": True,
        "expires_at": "2026-10-30T00:00:00+00:00",
        "grant_version": 1,
    }
    grant = {
        "tenant_id": tenant_id,
        "grant_id": grant_id,
        "version": 1,
        "status": "active",
        "mode": "apply",
        "expires_at": "2026-10-30T00:00:00+00:00",
        "plan_id": "plan-1",
        "node_id": "node-1",
        "phase_revision": 3,
        "model": MODEL,
        "allowed_actions": ["plan.priorities"],
        "budget": saved_budget,
    }
    actor = Actor.user(1)
    with scope.environment(PROJECT):
        control_entries.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorCredential", actor=actor, data=credential, idempotency=f"supervisor:credential:{credential_hash}"), actor)
        control_entries.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorEnrollment", actor=actor, data={"tenant_id": tenant_id, "enrollment_id": "enrollment-1", "plan_id": "plan-1", "node_id": "node-1", "status": "active"}, idempotency="supervisor:enrollment:tenant-a:plan-1:node-1"), actor)
        control_entries.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorGrant", actor=actor, data=grant, idempotency="supervisor:grant:tenant-a:grant-a:1"), actor)
    admissions = SupervisorAdmissions(entries, prices or {MODEL: ("0.10", "0.20")}, lambda: clock[0])
    return admissions, entries, scope, clock, grant, credential_hash


def observation(now, *, work_count=1, eligible=True, phase_revision=3, gates=None):
    return {
        "episode_id": "episode-1",
        "problem_fingerprint": "check:broken:revision-4",
        "evidence_generation": 2,
        "observed_at": now.isoformat(),
        "work_count": work_count,
        "phase_revision": phase_revision,
        "eligible": eligible,
        "gates": gates if gates is not None else {"plan_active": True, "phase_open": True},
    }


def claim_run(admissions, token=TOKEN, source="timer", event_id="event-1", facts=None):
    installation = admissions.start_installation(token, "boot-1")
    now = admissions.clock()
    run = admissions.admit_run(token, installation["epoch"], source, event_id, facts or observation(now))
    return installation, run


def measured_run(admissions, token=TOKEN, source="timer", event_id="event-1", facts=None):
    installation, run = claim_run(admissions, token, source, event_id, facts)
    admissions.begin_run(token, run["run_ref"], run["fence"])
    usage = admissions.record_usage(run["run_ref"], {"turns": 1, "input_tokens": 100, "output_tokens": 50})
    assert usage["status"] == "known"
    return installation, run


def action_intent(text="move diagnostic work first"):
    return {"episode_id": "episode-1", "kind": "plan.priorities", "grant_version": 1, "expected_revisions": {"phase": 3}, "payload": {"text": text}}


def mutation(entries, scope, intent, actor):
    with scope.environment(PROJECT):
        row = entries.save(Entry(environment_id=PROJECT, entry_type="SupervisorMutation", actor=actor, data={"action_id": intent["payload"]["text"]}), actor)
    return {"mutation_id": row.id}


def test_duplicate_action_returns_one_canonical_receipt(connection, bus, scope):
    admissions, entries, scope, _, _, _ = supervisor_journal(connection, bus, scope)
    installation, run = measured_run(admissions, source="hook")
    intent = action_intent()
    assert admissions.admit_action(TOKEN, run["run_ref"], run["fence"], "action-1", intent)["status"] == "admitted"
    calls = []

    def apply(values, actor):
        calls.append(values)
        return mutation(entries, scope, values, actor)

    receipt = admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-1", intent, lambda *_: None, apply)
    reordered = {"payload": {"text": "move diagnostic work first"}, "expected_revisions": {"phase": 3}, "grant_version": 1, "kind": "plan.priorities", "episode_id": "episode-1"}
    deliveries = [admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-1", reordered, lambda *_: None, apply) for _ in range(100)]
    assert receipt["status"] == "applied"
    assert all(result["receipt_id"] == receipt["receipt_id"] and result["data"] == receipt["data"] for result in deliveries)
    assert len(calls) == 1
    with scope.environment(PROJECT):
        assert len(entries.kind_entries("SupervisorMutation")) == 1


def test_reused_id_with_different_intent_is_rejected(connection, bus, scope):
    admissions, _, _, _, _, _ = supervisor_journal(connection, bus, scope)
    _, run = measured_run(admissions)
    first = action_intent()
    changed = action_intent("deploy the plan")
    assert admissions.admit_action(TOKEN, run["run_ref"], run["fence"], "action-2", first)["status"] == "admitted"
    rejected = admissions.admit_action(TOKEN, run["run_ref"], run["fence"], "action-2", changed)
    assert rejected["status"] == "rejected"
    assert rejected["data"]["reason"] == "action_id_reused"
    canonical = admissions.admit_action(TOKEN, run["run_ref"], run["fence"], "action-2", first)
    assert canonical["data"]["intent"] == first


def test_concurrent_admission_gets_one_fenced_run(connection, bus, scope):
    admissions, _, _, clock, _, _ = supervisor_journal(connection, bus, scope)
    installation = admissions.start_installation(TOKEN, "boot-1")
    facts = observation(clock[0])

    def claim(index):
        return admissions.admit_run(TOKEN, installation["epoch"], "timer", f"tick-{index}", facts)

    with ThreadPoolExecutor(max_workers=8) as workers:
        results = list(workers.map(claim, range(24)))
    admitted = [result for result in results if result["status"] == "admitted"]
    assert len(admitted) == 1
    assert admitted[0]["fence"] == 1
    assert {result.get("reason") for result in results if result["status"] == "skip"} == {"overlapping_run"}


def test_new_installation_advances_fence_and_does_not_wait_for_old_lease(connection, bus, scope):
    admissions, _, _, clock, _, _ = supervisor_journal(connection, bus, scope)
    _, old_run = measured_run(admissions)
    next_installation = admissions.start_installation(TOKEN, "boot-2")
    current = admissions.admit_run(TOKEN, next_installation["epoch"], "hook", "event-2", observation(clock[0]))
    assert next_installation["epoch"] == old_run["epoch"] + 1
    assert current["status"] == "admitted"
    assert current["fence"] == old_run["fence"] + 1
    stale_action = admissions.admit_action(TOKEN, old_run["run_ref"], old_run["fence"], "old-epoch-action", action_intent())
    assert stale_action["status"] == "rejected"
    assert stale_action["data"]["reason"] == "stale_installation_epoch"


def test_only_one_active_supervisor_can_claim_an_enrolled_plan_node(connection, bus, scope):
    admissions, entries, scope, clock, _, _ = supervisor_journal(connection, bus, scope)
    actor = Actor.user(1)
    with scope.environment(PROJECT):
        SupervisorEntries(entries).recorded(Entry(environment_id=PROJECT, entry_type="SupervisorGrant", actor=actor, data={"tenant_id": "tenant-a", "grant_id": "grant-b", "version": 1, "status": "active", "plan_id": "plan-1", "node_id": "node-1"}, idempotency="supervisor:grant:tenant-a:grant-b:1"), actor)
    installation = admissions.start_installation(TOKEN, "boot-1")
    assert installation == {"status": "rejected", "reason": "active_supervisor_not_unique"}
    run = admissions.admit_run(TOKEN, 1, "timer", "event-1", observation(clock[0]))
    assert run == {"status": "rejected", "reason": "active_supervisor_not_unique"}


@pytest.mark.parametrize("change,expected", [("revoke", "credential_revoked"), ("fence", "stale_fence")])
def test_revocation_or_stale_fence_prevents_apply(connection, bus, scope, change, expected):
    admissions, entries, scope, clock, _, credential_hash = supervisor_journal(connection, bus, scope)
    _, run = measured_run(admissions)
    intent = action_intent()
    admissions.admit_action(TOKEN, run["run_ref"], run["fence"], "action-3", intent)
    if change == "revoke":
        actor = Actor.system()
        with scope.environment(PROJECT):
            SupervisorEntries(entries).recorded(Entry(environment_id=PROJECT, entry_type="SupervisorRevocation", actor=actor, data={"tenant_id": "tenant-a", "credential_hash": credential_hash}, idempotency=f"supervisor:revoked:{credential_hash}"), actor)
    else:
        clock[0] += timedelta(seconds=301)
        admissions.admit_run(TOKEN, run["epoch"], "timer", "event-2", observation(clock[0]))
    called = []
    result = admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-3", intent, lambda *_: None, lambda *_: called.append(True))
    assert result["status"] in ("conflicted", "rejected")
    assert result["data"]["reason"] == expected
    assert called == []


def test_budget_is_reserved_before_model_and_unknown_usage_blocks(connection, bus, scope):
    budget = {
        "daily_cost_usd": "0.020",
        "daily_turns": 6,
        "daily_input_tokens": 144000,
        "daily_output_tokens": 48000,
        "input_tokens_per_turn": 24000,
        "output_tokens_per_turn": 8000,
        "max_retries": 2,
    }
    admissions, entries, _, clock, _, _ = supervisor_journal(connection, bus, scope, budget=budget)
    installation, run = claim_run(admissions)
    assert run["status"] == "admitted"
    assert run["data"]["reservation"] == {"cost_usd": "0.012000", "turns": 3, "input_tokens": 72000, "output_tokens": 24000, "input_rate_per_million": "0.10", "output_rate_per_million": "0.20", "max_retries": 2}
    unknown = admissions.record_usage(run["run_ref"], None)
    assert unknown["status"] == "pending"
    with scope.environment(PROJECT):
        usage_states = entries.supervisor_records("SupervisorUsage", tenant_id="tenant-a", run_ref=run["run_ref"])
    assert usage_states[0].data["reason"] == "usage_unknown"
    pending_action = admissions.admit_action(TOKEN, run["run_ref"], run["fence"], "budget-action", action_intent())
    assert pending_action["status"] == "pending"
    mutations = []
    premature = admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "budget-action", action_intent(), lambda *_: None, lambda *_: mutations.append(True))
    assert premature["status"] == "pending"
    assert mutations == []
    with scope.environment(PROJECT):
        assert not entries.supervisor_records("SupervisorActionReceipt", tenant_id="tenant-a", action_id="budget-action")
    no_price = SupervisorAdmissions(entries, {}, lambda: clock[0])
    assert no_price.admit_run(TOKEN, installation["epoch"], "hook", "unknown-price-event", observation(clock[0]))["reason"] == "unknown_model_price"
    admissions.finish_run(TOKEN, run["run_ref"], run["fence"])
    clock[0] += timedelta(seconds=1)
    blocked = admissions.admit_run(TOKEN, installation["epoch"], "timer", "event-2", observation(clock[0]))
    assert blocked["status"] == "skip"
    assert blocked["reason"] == "budget_exhausted"
    assert admissions.record_usage(run["run_ref"], {"turns": 1, "input_tokens": 100, "output_tokens": 50})["status"] == "known"
    released = admissions.admit_run(TOKEN, installation["epoch"], "timer", "event-3", observation(clock[0]))
    assert released["status"] == "admitted"


def test_revision_and_gate_conflicts_prevent_domain_mutation(connection, bus, scope):
    admissions, entries, scope, _, _, _ = supervisor_journal(connection, bus, scope)
    _, run = measured_run(admissions)
    intent = action_intent()
    admissions.admit_action(TOKEN, run["run_ref"], run["fence"], "action-gated", intent)
    validations = []
    mutations = []

    def conflict(values, grant, claimed_run):
        validations.append((values, grant, claimed_run))
        return {"status": "conflicted", "reason": "gate_closed"}

    result = admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-gated", intent, conflict, lambda *_: mutations.append(True))
    assert result["status"] == "conflicted"
    assert result["data"]["reason"] == "gate_closed"
    assert validations and mutations == []
    with scope.environment(PROJECT):
        states = entries.supervisor_records("SupervisorActionState", tenant_id="tenant-a", action_id="action-gated")
    assert {state.data["status"] for state in states} == {"pending", "conflicted"}


def test_empty_stale_and_ineligible_runs_skip_without_a_model(connection, bus, scope):
    admissions, entries, scope, clock, _, _ = supervisor_journal(connection, bus, scope)
    installation = admissions.start_installation(TOKEN, "boot-1")
    cases = (
        (observation(clock[0], work_count=0), "empty_work"),
        ({**observation(clock[0]), "observed_at": (clock[0] - timedelta(seconds=601)).isoformat()}, "stale_observation"),
        (observation(clock[0], eligible=False), "ineligible_work"),
        (observation(clock[0], phase_revision=2), "stale_phase_revision"),
        (observation(clock[0], gates={"phase_open": False}), "ineligible_gate"),
    )
    for index, (facts, reason) in enumerate(cases):
        result = admissions.admit_run(TOKEN, installation["epoch"], "hook", f"event-{index}", facts)
        assert result == {"status": "skip", "reason": reason}
    with scope.environment(PROJECT):
        assert not entries.supervisor_records("SupervisorRun", tenant_id="tenant-a")


def test_crash_before_commit_retries_without_partial_journal_mutation(connection, bus, scope):
    admissions, entries, scope, _, _, _ = supervisor_journal(connection, bus, scope)
    _, run = measured_run(admissions)
    intent = action_intent()
    admissions.admit_action(TOKEN, run["run_ref"], run["fence"], "action-4", intent)

    def crash(values, actor):
        mutation(entries, scope, values, actor)
        raise RuntimeError("crash before commit")

    with pytest.raises(RuntimeError, match="crash before commit"):
        admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-4", intent, lambda *_: None, crash)
    with scope.environment(PROJECT):
        assert not entries.kind_entries("SupervisorMutation")
        assert not entries.supervisor_records("SupervisorActionReceipt", tenant_id="tenant-a", action_id="action-4")
        assert not entries.supervisor_records("SupervisorActionState", tenant_id="tenant-a", action_id="action-4", status="pending")
    applied = admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-4", intent, lambda *_: None, lambda values, actor: mutation(entries, scope, values, actor))
    assert applied["status"] == "applied"
    with scope.environment(PROJECT):
        assert len(entries.kind_entries("SupervisorMutation")) == 1


def test_commit_with_lost_response_returns_prior_receipt(connection, bus, scope):
    admissions, entries, scope, _, _, _ = supervisor_journal(connection, bus, scope)
    _, run = measured_run(admissions)
    intent = action_intent()
    admissions.admit_action(TOKEN, run["run_ref"], run["fence"], "action-5", intent)
    calls = []

    def apply(values, actor):
        calls.append(True)
        return mutation(entries, scope, values, actor)

    first = admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-5", intent, lambda *_: None, apply)
    retry = admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-5", intent, lambda *_: None, apply)
    assert retry["receipt_id"] == first["receipt_id"]
    assert retry["data"] == first["data"]
    assert len(calls) == 1


def test_receipt_tombstone_survives_trim_and_restart(connection, bus, scope, tmp_path):
    admissions, entries, scope, clock, _, _ = supervisor_journal(connection, bus, scope)
    _, run = measured_run(admissions)
    intent = action_intent()
    admissions.admit_action(TOKEN, run["run_ref"], run["fence"], "action-6", intent)
    calls = []

    def apply(values, actor):
        calls.append(True)
        return mutation(entries, scope, values, actor)

    receipt = admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-6", intent, lambda *_: None, apply)
    with scope.environment(PROJECT):
        entries.trim(entries.last_id(), 0)
    connection.close()
    restarted = Connection(connection.path, Masks(SecretValues(Config(tmp_path))), StageTimes(), QueryTimes(), LargeReads())
    restarted_scope = Scope(Environments(restarted, bus, TimeSource()), Links(restarted, bus, TimeSource()))
    restarted_entries = Entries(restarted, bus, restarted_scope, TimeSource())
    restarted_admissions = SupervisorAdmissions(restarted_entries, {MODEL: ("0.10", "0.20")}, lambda: clock[0])
    installation = restarted_admissions.start_installation(TOKEN, "boot-2")
    assert installation["epoch"] > run["epoch"]
    retry = restarted_admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-6", intent, lambda *_: None, lambda *_: calls.append(True))
    assert retry["receipt_id"] == receipt["receipt_id"]
    assert retry["data"] == receipt["data"]
    assert len(calls) == 1
    restarted.close()


def test_run_retries_stop_at_the_granted_cap(connection, bus, scope):
    admissions, _, _, _, _, _ = supervisor_journal(connection, bus, scope)
    _, run = claim_run(admissions)
    assert admissions.begin_run(TOKEN, run["run_ref"], run["fence"])["status"] == "pending"
    assert admissions.retry_run(TOKEN, run["run_ref"], run["fence"], "retry-1")["data"]["retry_count"] == 1
    assert admissions.retry_run(TOKEN, run["run_ref"], run["fence"], "retry-2")["data"]["retry_count"] == 2
    rejected = admissions.retry_run(TOKEN, run["run_ref"], run["fence"], "retry-3")
    assert rejected == {"status": "rejected", "reason": "retry_limit_exhausted"}
