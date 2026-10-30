from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import uuid4

import pytest

from journal.config import Config
from journal.db.connection import Connection
from journal.events.rows.check_completed import CheckCompleted
from journal.features.supervisor.support.supervisor_maintenance import SupervisorMaintenance, diagnostic_task_values
from journal.features.supervisor.support.supervisor_observations import SupervisorObservations
from journal.models.entry import Entry
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.user import User
from journal.models.worker import Worker
from journal.repositories.checks import Checks
from journal.repositories.environment_owners import OWNER
from journal.repositories.environments import Environments
from journal.repositories.entries import Entries
from journal.repositories.links import Links
from journal.repositories.plans import Plans
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.repositories.tasks import CURRENT_TASK_LINK, Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.large_reads import LargeReads
from journal.support.masks import Masks
from journal.support.query_times import QueryTimes
from journal.support.secret_values import SecretValues
from journal.support.stage_times import StageTimes
from journal.support.time_source import TimeSource
from journal.features.supervisor.support.admissions import SupervisorAdmissions
from journal.supervisor_failure import SupervisorFailure
from tests.suite_app import SuiteApp
from tests.test_supervisor_authority import (
    admitted as authority_admitted,
    enrollment as authority_enrollment,
    seeded as authority_seeded,
)


TOKEN = "supervisor-credential-for-tests"
NOW = datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc)
MODEL = "test/model"


@pytest.fixture(scope="module")
def boot():
    return lambda root, patch: SuiteApp(Config(root, port=0))


def maintenance_context(app, monkeypatch, mode="bounded_write"):
    fixture = authority_seeded(app, owner_id=uuid4().int % 1_000_000 + 100)
    return _admitted_maintenance_context(app, monkeypatch, fixture, mode)


def maintenance_context_with_existing_diagnostic(app, monkeypatch):
    fixture = authority_seeded(app, owner_id=uuid4().int % 1_000_000 + 100)
    title, brief = diagnostic_task_values(fixture.template)
    plans = app.container.get(Plans)
    tasks = app.container.get(Tasks)
    with app.container.get(Scope).environment(fixture.owner_environment.row_id):
        diagnostic = tasks.save(Task(environment_id=fixture.owner_environment.row_id, title=title, brief=brief), fixture.owner)
        plans.place_task_in_phase(diagnostic, fixture.plan, fixture.phase, fixture.owner)
    context = _admitted_maintenance_context(app, monkeypatch, fixture, "bounded_write")
    context["existing_diagnostic"] = diagnostic
    return context


def maintenance_context_with_held_diagnostic(app, monkeypatch):
    fixture = authority_seeded(app, owner_id=uuid4().int % 1_000_000 + 100)
    title, brief = diagnostic_task_values(fixture.template)
    plans = app.container.get(Plans)
    tasks = app.container.get(Tasks)
    links = app.container.get(Links)
    with app.container.get(Scope).environment(fixture.owner_environment.row_id):
        diagnostic = tasks.save(Task(environment_id=fixture.owner_environment.row_id, title=title, brief=brief, delegated=True), fixture.owner)
        plans.place_task_in_phase(diagnostic, fixture.plan, fixture.phase, fixture.owner)
        worker = app.container.get(Workers).save(Worker(environment_id=fixture.owner_environment.row_id, name="maintenance holder", brief="hold diagnostic"), Actor.system())
        links.save(Link(source=Ref.build(worker), target=Ref.build(diagnostic), link_type=CURRENT_TASK_LINK), Actor.system())
    context = _admitted_maintenance_context(app, monkeypatch, fixture, "bounded_write")
    context["held_diagnostic"] = diagnostic
    return context


def _admitted_maintenance_context(app, monkeypatch, fixture, mode):
    monkeypatch.setattr(fixture.authority.agents, "is_running", lambda _environment: True)
    grant, token, principal = authority_admitted(fixture, mode)
    entries = app.container.get(Entries)
    control_entries = app.container.get(SupervisorEntries)
    scope = app.container.get(Scope)
    time_source = app.container.get(TimeSource)
    actor = principal.actor
    now = datetime.fromtimestamp(time_source.seconds(), timezone.utc)
    run_id = uuid4().hex
    with scope.environment(PROJECT):
        control_entries.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorInstallation", actor=actor,
            data={"tenant_id": principal.scope["tenant_id"], "grant_id": grant["grant_id"],
                "installation_id": "maintenance-test", "epoch": principal.scope["installation_epoch"]},
            idempotency=f"supervisor:installation:{principal.scope['tenant_id']}:maintenance-test"), actor)
        run = control_entries.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorRun", actor=actor,
            data={"tenant_id": principal.scope["tenant_id"], "grant_id": grant["grant_id"],
                "grant_version": grant["grant_version"], "plan_id": grant["plan_id"],
                "node_id": principal.scope["writer_node_id"], "episode_id": "episode-maintenance",
                "run_ref": run_id, "installation_epoch": principal.scope["installation_epoch"],
                "fence": 1, "lease_until": (now + timedelta(minutes=5)).isoformat(), "status": "admitted"},
            idempotency=f"supervisor:run:{principal.scope['tenant_id']}:{run_id}"), actor)
        control_entries.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorEpisode", actor=actor,
            data={"tenant_id": principal.scope["tenant_id"], "plan_id": grant["plan_id"],
                "episode_id": "episode-maintenance", "evidence_generation": 1,
                "problem_fingerprint": "check:health:failed"},
            idempotency=f"supervisor:episode:{principal.scope['tenant_id']}:{grant['plan_id']}:episode-maintenance"), actor)
        control_entries.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorUsage", actor=actor,
            data={"tenant_id": principal.scope["tenant_id"], "run_ref": run_id, "status": "known",
                "turns": 1, "input_tokens": 100, "output_tokens": 50, "cost_usd": "0.000001", "overrun": False},
            idempotency=f"supervisor:usage:{principal.scope['tenant_id']}:{run_id}"), actor)
    observations = app.container.get(SupervisorObservations)
    checks = app.container.get(Checks)
    check = checks.find(fixture.check.row_id)
    observed_at = time_source.seconds()
    event = CheckCompleted(environment_id=fixture.owner_environment.row_id, time=observed_at,
        check_id=check.row_id, title=check.title, passed=False, output="health check failed",
        prior_failure=False, wait_target=False, failure_reported_at=0)
    observations.completed(check, event, observed_at - 1, "")
    with scope.environment(PROJECT):
        evidence = entries.supervisor_records("SupervisorObservation", last=100,
            grant_id=grant["grant_id"], grant_version=grant["grant_version"], check_id=check.row_id)
    maintenance = app.container.get(SupervisorMaintenance)
    return {"fixture": fixture, "grant": grant, "token": token, "principal": principal,
        "run": run, "evidence": evidence[-1], "maintenance": maintenance,
        "entries": entries, "scope": scope, "time_source": time_source}


@pytest.fixture
def bounded_maintenance(app, monkeypatch):
    fixture = maintenance_context(app, monkeypatch)
    yield fixture
    fixture["fixture"].authority.secrets_store.drop(fixture["fixture"].credentials)


@pytest.fixture
def shadow_maintenance(app, monkeypatch):
    fixture = maintenance_context(app, monkeypatch, "shadow")
    yield fixture
    fixture["fixture"].authority.secrets_store.drop(fixture["fixture"].credentials)


@pytest.fixture
def existing_diagnostic_maintenance(app, monkeypatch):
    fixture = maintenance_context_with_existing_diagnostic(app, monkeypatch)
    yield fixture
    fixture["fixture"].authority.secrets_store.drop(fixture["fixture"].credentials)


@pytest.fixture
def held_diagnostic_maintenance(app, monkeypatch):
    fixture = maintenance_context_with_held_diagnostic(app, monkeypatch)
    yield fixture
    fixture["fixture"].authority.secrets_store.drop(fixture["fixture"].credentials)


def maintenance_request(context, operations, action_id=None):
    fixture, grant, principal = context["fixture"], context["grant"], context["principal"]
    authority = fixture.authority
    current = authority.action_context(principal)[1]
    expected = [
        {"ref": {"table": "plans", "id": grant["plan_id"]}, "revision": current["plan_revision"]},
        {"ref": {"table": "phases", "id": current["current_phase"]["phase_id"]},
            "revision": current["current_phase"]["revision"]},
    ]
    for operation in operations:
        if operation["kind"] == "check_interval":
            check = context["maintenance"].checks.find(operation["check_id"])
            expected.append({"ref": {"table": "checks", "id": check.row_id},
                "revision": authority.check_action_revision(check)})
    return {
        "protocol_version": 1,
        "run_id": context["run"].data["run_ref"],
        "installation_epoch": principal.scope["installation_epoch"],
        "fence": context["run"].data["fence"],
        "grant_version": grant["grant_version"],
        "episode_id": context["run"].data["episode_id"],
        "action_id": action_id or f"action-{uuid4().hex}",
        "observation_ids": [context["evidence"].data["observation_id"]],
        "expected_revisions": expected,
        "operations": operations,
        "rationale": "A bounded maintenance test action.",
    }


def diagnostic_operation(context, evidence_ids=None):
    grant = context["grant"]
    return {"kind": "diagnostic_task", "plan_id": grant["plan_id"],
        "phase_id": grant["current_phase"]["phase_id"],
        "template_id": grant["diagnostic_template_id"],
        "template_revision": grant["diagnostic_template_revision"],
        "evidence_ids": evidence_ids or [context["evidence"].data["observation_id"]]}


def test_bundle_uses_same_plan_current_phase_and_existing_diagnostic(existing_diagnostic_maintenance):
    context = existing_diagnostic_maintenance
    fixture = context["fixture"]
    operations = [
        diagnostic_operation(context),
        {"kind": "plan_priorities", "plan_id": context["grant"]["plan_id"], "text": "Check the failure\nThen report the cause"},
    ]
    request = maintenance_request(context, operations)
    with context["scope"].environment(fixture.owner_environment.row_id):
        before_tasks = [task.row_id for task in context["maintenance"].plans.plan_tasks(fixture.plan)]
    receipt = context["maintenance"].apply_maintenance(context["principal"], request)
    with context["scope"].environment(fixture.owner_environment.row_id):
        plan = context["maintenance"].plans.find(fixture.plan.row_id)
        tasks = context["maintenance"].plans.plan_tasks(plan)
        phase_tasks = context["maintenance"].plans.phase_tasks(fixture.phase)
        current_phase = plan.current_phase(context["maintenance"].plans.phase_states(plan))
    assert receipt["status"] == "applied"
    assert receipt["data"]["verification"] == "verified"
    assert plan.priorities == "Check the failure\nThen report the cause"
    assert current_phase == context["grant"]["current_phase"]["number"]
    assert context["existing_diagnostic"] in phase_tasks
    assert {task.row_id for task in tasks} == set(before_tasks)
    assert {("tasks", context["existing_diagnostic"].row_id), ("plans", fixture.plan.row_id),
        ("phases", fixture.phase.row_id)} <= {
            (item["table"], item["id"]) for item in receipt["data"]["affected_refs"]
        }
    assert [change["field"] for change in receipt["data"]["changes"]] == ["priorities"]


def test_retried_maintenance_action_returns_its_receipt_without_adding_a_second_diagnostic(bounded_maintenance):
    context = bounded_maintenance
    fixture = context["fixture"]
    request = maintenance_request(context, [diagnostic_operation(context)])
    first = context["maintenance"].apply_maintenance(context["principal"], request)
    with context["scope"].environment(fixture.owner_environment.row_id):
        task_ids = {task.row_id for task in context["maintenance"].plans.plan_tasks(fixture.plan)}
    retry = context["maintenance"].apply_maintenance(context["principal"], request)
    with context["scope"].environment(fixture.owner_environment.row_id):
        retry_task_ids = {task.row_id for task in context["maintenance"].plans.plan_tasks(fixture.plan)}
    assert retry["duplicate"]
    assert retry["receipt_id"] == first["receipt_id"]
    assert retry["data"] == first["data"]
    assert retry_task_ids == task_ids


@pytest.mark.parametrize("edit", ("phase", "owner"))
def test_phase_or_owner_edit_conflicts_entire_bundle(bounded_maintenance, edit):
    context = bounded_maintenance
    fixture = context["fixture"]
    operations = [
        {"kind": "plan_priorities", "plan_id": context["grant"]["plan_id"], "text": "Check the failure first"},
        {"kind": "check_interval", "check_id": fixture.check.row_id, "interval_minutes": 5},
    ]
    request = maintenance_request(context, operations)
    links = context["maintenance"].links
    with context["scope"].environment(fixture.owner_environment.row_id):
        plan_before = context["maintenance"].plans.find(fixture.plan.row_id)
        check_before = context["maintenance"].checks.find(fixture.check.row_id)
        if edit == "phase":
            context["maintenance"].plans.phases.save(fixture.phase.with_(title="Edited current phase"), fixture.owner)
        else:
            for link in links.matching(target=Ref.build(fixture.owner_environment), link_type=OWNER):
                links.delete(link, Actor.system())
            links.linked(Ref.build(User(id=2)), Ref.build(fixture.owner_environment), OWNER, Actor.system())
    receipt = context["maintenance"].apply_maintenance(context["principal"], request)
    with context["scope"].environment(fixture.owner_environment.row_id):
        plan_after = context["maintenance"].plans.find(fixture.plan.row_id)
        check_after = context["maintenance"].checks.find(fixture.check.row_id)
    assert receipt["status"] == "conflicted"
    assert plan_after.priorities == plan_before.priorities
    assert check_after.interval == check_before.interval
    assert not receipt["data"]["affected_refs"]
    assert not receipt["data"]["changes"]


def test_check_interval_changes_without_changing_command_or_result(bounded_maintenance):
    context = bounded_maintenance
    fixture = context["fixture"]
    before = context["maintenance"].checks.find(fixture.check.row_id)
    request = maintenance_request(context, [{
        "kind": "check_interval", "check_id": before.row_id, "interval_minutes": 5,
    }])
    receipt = context["maintenance"].apply_maintenance(context["principal"], request)
    after = context["maintenance"].checks.find(before.row_id)
    change = next(change for change in receipt["data"]["changes"] if change["field"] == "interval")
    assert receipt["status"] == "applied"
    assert after.interval == 5
    assert after.command == before.command
    assert (after.verdict(), after.last_passed, after.last_output, after.last_run_at, after.last_report,
        after.last_duration, after.last_fault, after.failure_reported_at, after.last_stopped, after.progress) == (
            before.verdict(), before.last_passed, before.last_output, before.last_run_at, before.last_report,
            before.last_duration, before.last_fault, before.failure_reported_at, before.last_stopped, before.progress)
    assert change["ref"] == {"table": "checks", "id": before.row_id}
    assert change["before_revision"] == fixture.authority.check_action_revision(before)
    assert change["after_revision"] == fixture.authority.check_action_revision(after)
    assert {"table": "checks", "id": before.row_id} in receipt["data"]["affected_refs"]


def test_held_tasks_and_disabled_operations_are_untouched(held_diagnostic_maintenance):
    context = held_diagnostic_maintenance
    fixture = context["fixture"]
    held = context["held_diagnostic"]
    request = maintenance_request(context, [diagnostic_operation(context)])
    disabled = maintenance_request(context, [{"kind": "sequence", "sequence_id": "not-enabled"}])
    receipt = context["maintenance"].apply_maintenance(context["principal"], request)
    with context["scope"].environment(fixture.owner_environment.row_id):
        tasks = context["maintenance"].plans.phase_tasks(fixture.phase)
        held_after = context["maintenance"].tasks.find(held.row_id)
    created = next(task for task in tasks if task.row_id != held.row_id and task.title == held.title)
    assert receipt["status"] == "applied"
    assert held_after.delegated and held_after.state == held.state and held_after.brief == held.brief
    assert context["maintenance"].tasks.task_holder(held.row_id) is not None
    assert context["maintenance"].tasks.task_holder(created.row_id) is None
    phase_change = next(change for change in receipt["data"]["changes"] if change["field"] == "phase_link")
    assert phase_change["ref"] == {"table": "tasks", "id": created.row_id}
    assert phase_change["before_revision"] != phase_change["after_revision"]
    before_ids = {task.row_id for task in tasks}
    with context["scope"].environment(PROJECT):
        receipts_before = context["entries"].supervisor_records(
            "SupervisorActionReceipt", last=100, grant_id=context["grant"]["grant_id"],
        )
    for index, kind in enumerate(("sequence", "phrase_nudge", "project_reminder", "settings", "shell")):
        disabled["action_id"] = f"disabled-{index}-{uuid4().hex}"
        disabled["operations"] = [{"kind": kind, "value": "not-enabled"}]
        with pytest.raises(SupervisorFailure) as denied:
            context["maintenance"].apply_maintenance(context["principal"], disabled)
        assert denied.value.status == 400
    with context["scope"].environment(fixture.owner_environment.row_id):
        after_ids = {task.row_id for task in context["maintenance"].plans.phase_tasks(fixture.phase)}
    with context["scope"].environment(PROJECT):
        receipts_after = context["entries"].supervisor_records(
            "SupervisorActionReceipt", last=100, grant_id=context["grant"]["grant_id"],
        )
    assert after_ids == before_ids
    assert len(receipts_after) == len(receipts_before)


def test_shadow_records_only_proposal_receipts_without_domain_writes(shadow_maintenance):
    context = shadow_maintenance
    fixture = context["fixture"]
    operations = [
        diagnostic_operation(context),
        {"kind": "plan_priorities", "plan_id": context["grant"]["plan_id"], "text": "Check the failure first"},
        {"kind": "check_interval", "check_id": fixture.check.row_id, "interval_minutes": 5},
    ]
    request = maintenance_request(context, operations)
    with context["scope"].environment(fixture.owner_environment.row_id):
        plan_before = context["maintenance"].plans.find(fixture.plan.row_id)
        task_ids_before = {task.row_id for task in context["maintenance"].plans.plan_tasks(plan_before)}
        phase_ids_before = {task.row_id for task in context["maintenance"].plans.phase_tasks(fixture.phase)}
        check_before = context["maintenance"].checks.find(fixture.check.row_id)
    with context["scope"].environment(PROJECT):
        receipts_before = context["entries"].supervisor_records(
            "SupervisorActionReceipt", last=100, grant_id=context["grant"]["grant_id"],
        )
    receipt = context["maintenance"].apply_maintenance(context["principal"], request)
    with context["scope"].environment(fixture.owner_environment.row_id):
        plan_after = context["maintenance"].plans.find(fixture.plan.row_id)
        task_ids_after = {task.row_id for task in context["maintenance"].plans.plan_tasks(plan_after)}
        phase_ids_after = {task.row_id for task in context["maintenance"].plans.phase_tasks(fixture.phase)}
        check_after = context["maintenance"].checks.find(fixture.check.row_id)
    with context["scope"].environment(PROJECT):
        receipts_after = context["entries"].supervisor_records(
            "SupervisorActionReceipt", last=100, grant_id=context["grant"]["grant_id"],
        )
    assert receipt["status"] == "proposed"
    assert receipt["data"]["verification"] == "not_applied"
    assert receipt["data"]["affected_refs"] == [] and receipt["data"]["changes"] == []
    assert plan_after.priorities == plan_before.priorities
    assert task_ids_after == task_ids_before and phase_ids_after == phase_ids_before
    assert check_after.interval == check_before.interval
    assert len(receipts_after) == len(receipts_before) + 1
    assert receipts_after[0].data["status"] == "proposed"


def supervisor_journal(connection, bus, scope, budget=None, prices=None):
    entries = Entries(connection, bus, scope, TimeSource())
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
    control_entries = SupervisorEntries(entries)
    with scope.environment(PROJECT):
        control_entries.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorCredential", actor=actor, data=credential, idempotency=f"supervisor:credential:{credential_hash}"), actor)
        control_entries.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorEnrollment", actor=actor, data={"tenant_id": tenant_id, "enrollment_id": "enrollment-1", "plan_id": "plan-1", "node_id": "node-1", "status": "active"}, idempotency="supervisor:enrollment:tenant-a:plan-1:node-1"), actor)
        control_entries.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorGrant", actor=actor, data=grant, idempotency="supervisor:grant:tenant-a:grant-a:1"), actor)
    admissions = SupervisorAdmissions(entries, control_entries, prices or {MODEL: ("0.10", "0.20")}, lambda: clock[0])
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
        row = entries.save(Entry(environment_id=PROJECT, entry_type="ActionMutation", actor=actor, data={"action_id": intent["payload"]["text"]}), actor)
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
        assert len(entries.kind_entries("ActionMutation")) == 1


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
    no_price = SupervisorAdmissions(entries, SupervisorEntries(entries), {}, lambda: clock[0])
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
        assert not entries.kind_entries("ActionMutation")
        assert not entries.supervisor_records("SupervisorActionReceipt", tenant_id="tenant-a", action_id="action-4")
        assert not entries.supervisor_records("SupervisorActionState", tenant_id="tenant-a", action_id="action-4", status="pending")
    applied = admissions.apply_action(TOKEN, run["run_ref"], run["fence"], "action-4", intent, lambda *_: None, lambda values, actor: mutation(entries, scope, values, actor))
    assert applied["status"] == "applied"
    with scope.environment(PROJECT):
        assert len(entries.kind_entries("ActionMutation")) == 1


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
    restarted_admissions = SupervisorAdmissions(restarted_entries, SupervisorEntries(restarted_entries), {MODEL: ("0.10", "0.20")}, lambda: clock[0])
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


def test_owner_edit_prevents_rollback_and_is_preserved(bounded_maintenance):
    context = bounded_maintenance
    fixture = context["fixture"]
    original_interval = int(context["maintenance"].checks.find(fixture.check.row_id).interval)
    request = maintenance_request(context, [
        diagnostic_operation(context),
        {"kind": "plan_priorities", "plan_id": context["grant"]["plan_id"], "text": "Supervisor priority"},
        {"kind": "check_interval", "check_id": fixture.check.row_id, "interval_minutes": 5},
    ])
    receipt = context["maintenance"].apply_maintenance(context["principal"], request)
    diagnostic_id = next(item["id"] for item in receipt["data"]["affected_refs"] if item["table"] == "tasks")
    with context["scope"].environment(fixture.owner_environment.row_id):
        plan = context["maintenance"].plans.find(fixture.plan.row_id)
        context["maintenance"].plans.save(plan.prioritised("Owner priority", context["grant"]["current_phase"]["number"], context["time_source"].seconds()), fixture.owner)
        diagnostic = context["maintenance"].tasks.find(diagnostic_id)
        context["maintenance"].tasks.assign_holder(diagnostic, Ref.build(fixture.agent), Actor.system())

    rollback = context["maintenance"].rollback(context["principal"], receipt["receipt_id"])
    with context["scope"].environment(fixture.owner_environment.row_id):
        plan = context["maintenance"].plans.find(fixture.plan.row_id)
        diagnostic = context["maintenance"].tasks.find(diagnostic_id)
        phase_tasks = context["maintenance"].plans.phase_tasks(fixture.phase)
        check = context["maintenance"].checks.find(fixture.check.row_id)
    assert rollback["data"]["status"] == "applied"
    assert rollback["report"]["rollback"]["status"] == "needs_owner"
    assert rollback["report"]["rollback"]["reason"] == "owner_edit_preserved"
    assert plan.priorities == "Owner priority", "conditional rollback preserves the current owner value"
    assert int(check.interval) == original_interval, "conditional rollback restores an unchanged permitted field"
    assert diagnostic in phase_tasks and context["maintenance"].tasks.task_holder(diagnostic_id) == Ref.build(fixture.agent), "rollback never removes or unassigns the diagnostic task"
    assert any(field["field"] == "interval" and field["status"] == "rolled_back"
               for field in rollback["report"]["rollback"]["fields"])


def test_restart_readback_finishes_applied_receipt_without_reapply(bounded_maintenance, monkeypatch):
    context = bounded_maintenance
    fixture = context["fixture"]
    maintenance = context["maintenance"]
    request = maintenance_request(context, [diagnostic_operation(context)], "restart-readback")
    original_reconcile = maintenance.reconcile_receipt
    monkeypatch.setattr(maintenance, "reconcile_receipt", lambda *_: (_ for _ in ()).throw(RuntimeError("restart before receipt readback")))
    with pytest.raises(RuntimeError, match="restart before receipt readback"):
        maintenance.apply_maintenance(context["principal"], request)

    with context["scope"].environment(fixture.owner_environment.row_id):
        task_ids_before = {task.row_id for task in maintenance.plans.plan_tasks(fixture.plan)}
    monkeypatch.setattr(maintenance, "reconcile_receipt", original_reconcile)
    receipt = maintenance.receipt(context["principal"], request["action_id"])
    with context["scope"].environment(fixture.owner_environment.row_id):
        task_ids_after = {task.row_id for task in maintenance.plans.plan_tasks(fixture.plan)}
    assert receipt["status"] == "applied" and receipt["data"]["verification"] == "verified"
    with context["scope"].environment(PROJECT):
        stored = context["entries"].supervisor_records("SupervisorActionReceipt", last=1, action_id=request["action_id"])[0]
    assert receipt["receipt_id"] == stored.row_id
    assert task_ids_after == task_ids_before, "receipt recovery reads back the committed diagnostic without applying it a second time"


def test_restore_new_epoch_rejects_old_callbacks_until_owner_reenables(bounded_maintenance):
    context = bounded_maintenance
    fixture = context["fixture"]
    authority = fixture.authority
    grant = context["grant"]
    request = maintenance_request(context, [diagnostic_operation(context)], "before-owner-review")
    authority.restore_installation(fixture.owner, grant["grant_id"])
    with pytest.raises(SupervisorFailure):
        context["maintenance"].apply_maintenance(context["principal"], request)
    with context["scope"].environment(PROJECT):
        disabled = context["entries"].supervisor_records("SupervisorInstallation", last=1, tenant_id=grant["scope"]["tenant_id"])[0]
        assert disabled.data["management_writes_enabled"] is False
        assert disabled.data["evidence_watermark_ms"] is not None
        assert disabled.data["evidence_rpo_gap_ms"] is None
        assert disabled.data["evidence_rpo_gap_reason"] == "restore_point_time_unavailable"

    replacement = {
        "protocol_version": 1,
        "grant_id": grant["grant_id"],
        "expected_grant_version": grant["grant_version"],
        "change": {"kind": "replace", "enrollment": authority_enrollment(fixture, "bounded_write")},
    }
    before_review = context["entries"].global_last_id()
    with pytest.raises(SupervisorFailure, match="evidence and RPO gap require owner review"):
        authority.change(fixture.owner, replacement)
    assert context["entries"].global_last_id() == before_review, "reenabling requires an explicit evidence review and does not write on refusal"
    replacement["change"]["restore_review"] = {
        "epoch": disabled.data["epoch"],
        "evidence_watermark_ms": disabled.data["evidence_watermark_ms"],
        "evidence_rpo_gap_ms": disabled.data["evidence_rpo_gap_ms"],
        "accept_unavailable_evidence": True,
    }
    current, token = authority.change(fixture.owner, replacement)
    principal = authority.authenticate(token)
    with context["scope"].environment(PROJECT):
        enabled = context["entries"].supervisor_records("SupervisorInstallation", last=1, tenant_id=grant["scope"]["tenant_id"])[0]
    assert current["grant_version"] == grant["grant_version"] + 1 and principal.scope["installation_epoch"] == disabled.data["epoch"]
    assert enabled.data["management_writes_enabled"] is True and enabled.data["owner_reviewed_at_ms"] > 0
    with pytest.raises(SupervisorFailure):
        authority.authenticate(context["token"])


def test_applied_receipt_measures_check_and_task_evidence_separately(bounded_maintenance):
    context = bounded_maintenance
    fixture = context["fixture"]
    maintenance = context["maintenance"]
    request = maintenance_request(context, [diagnostic_operation(context),
        {"kind": "plan_priorities", "plan_id": context["grant"]["plan_id"], "text": "Check evidence then inspect the diagnostic"}],
        "independent-evidence")
    receipt = maintenance.apply_maintenance(context["principal"], request)
    assert receipt["status"] == "applied" and receipt["data"]["verification"] == "verified"
    assert receipt["data"]["outcome"] == "unmeasured"
    diagnostic_id = next(item["id"] for item in receipt["data"]["affected_refs"] if item["table"] == "tasks")

    start = context["time_source"].seconds()
    observations = maintenance.observations
    check = maintenance.checks.find(fixture.check.row_id)
    passed = CheckCompleted(environment_id=fixture.owner_environment.row_id, time=start + 1,
        check_id=check.row_id, title=check.title, passed=True, output="health check passed",
        prior_failure=True, wait_target=False, failure_reported_at=0)
    with context["scope"].environment(fixture.owner_environment.row_id):
        observations.completed(check, passed, start, "")
    after_check = maintenance.receipt(context["principal"], request["action_id"])
    assert after_check["status"] == "applied" and after_check["data"]["outcome"] == "useful_evidence"
    assert after_check["report"]["outcome_evidence"]["checks"][0]["check_id"] == fixture.check.row_id
    assert not after_check["report"]["outcome_evidence"]["tasks"]

    with context["scope"].environment(fixture.owner_environment.row_id):
        diagnostic = maintenance.tasks.find(diagnostic_id)
        maintenance.tasks.save(diagnostic.started(datetime.fromtimestamp(start + 2, timezone.utc)), Actor.agent(fixture.agent.session))
        check = maintenance.checks.find(fixture.check.row_id)
        failed = CheckCompleted(environment_id=fixture.owner_environment.row_id, time=start + 3,
            check_id=check.row_id, title=check.title, passed=False, output="health check still fails",
            prior_failure=True, wait_target=False, failure_reported_at=0)
        observations.completed(check, failed, start + 2, "")
    after_task = maintenance.receipt(context["principal"], request["action_id"])
    with context["scope"].environment(PROJECT):
        stored = context["entries"].supervisor_records("SupervisorActionReceipt", last=1,
            action_id=request["action_id"])[0]
    assert after_task["data"]["status"] == stored.data["status"] == "applied"
    assert stored.data["verification"] == "pending" and stored.data["outcome"] == "unmeasured"
    assert after_task["data"]["verification"] == "verified" and after_task["data"]["outcome"] == "useful_evidence"
    assert after_task["report"]["outcome_evidence"]["tasks"][0]["task_id"] == diagnostic_id
