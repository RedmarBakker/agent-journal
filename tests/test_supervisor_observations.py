import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone

import pytest

from journal.config import Config
from journal.db.connection import Connection
from journal.events.rows.check_completed import CheckCompleted
from journal.features.checks.support.check_output import CheckOutput
from journal.features.checks.support.check_runner import CheckRunner
from journal.features.checks.support.finished_run import FinishedRun
from journal.features.record.jobs.record_trim import RecordTrim
from journal.features.supervisor.support.supervisor_observations import EVIDENCE_RETENTION_MS, OBSERVATION_ENTRY, SupervisorObservations
from journal.features.supervisor.support.supervisor_episode_qualification import SupervisorEpisodeQualification
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.http.controllers.supervisor import SupervisorController
from journal.http.support.identity import Identity
from journal.http.support.request_reading import RequestReading
from journal.http.support.supervisor_authentication import SupervisorRequestAuth, TOKEN_HEADER
from journal.models.agent import Agent
from journal.models.check import Check
from journal.models.entry import Entry
from journal.models.phase import Phase
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.template import Template
from journal.models.user import User
from journal.repositories.agents import Agents
from journal.repositories.checks import Checks
from journal.repositories.entries import Entries
from journal.repositories.environment_owners import OWNER
from journal.repositories.environments import Environments
from journal.repositories.journal_backup import JournalBackup
from journal.repositories.links import Links
from journal.repositories.phases import PHASE_TASK_LINK, Phases
from journal.repositories.plans import PHASE_LINK, PLAN_LINK, Plans
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.repositories.tasks import Tasks
from journal.repositories.templates import Templates
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.support.secret_values import SecretValues
from journal.support.time_source import TimeSource
from journal.supervisor_authority import SupervisorAuthority
from tests.suite_app import SuiteApp


@pytest.fixture(scope="module")
def boot():
    def booted(root, patch):
        return SuiteApp(Config(root, port=0))
    return booted


@pytest.fixture
def supervisor_fixture(app, monkeypatch):
    fixture = seeded(app)
    monkeypatch.setattr(fixture["authority"].agents, "is_running", lambda _: True)
    yield fixture
    fixture["authority"].secrets_store.drop(fixture["credentials"])


def seeded(app, owner_id=1):
    actor = Actor.user(owner_id)
    scope = app.container.get(Scope)
    environments = app.container.get(Environments)
    links = app.container.get(Links)
    plans = app.container.get(Plans)
    phases = app.container.get(Phases)
    tasks = app.container.get(Tasks)
    checks = app.container.get(Checks)
    agents = app.container.get(Agents)
    templates = app.container.get(Templates)
    owner_environment = environments.made(f"observation-owner-{owner_id}", actor)
    driver_environment = environments.made(f"observation-driver-{owner_id}", actor)
    for environment in (owner_environment, driver_environment):
        for owner_link in links.matching(target=Ref.build(environment), link_type=OWNER):
            links.delete(owner_link, Actor.system())
        links.linked(Ref.build(User(id=owner_id)), Ref.build(environment), OWNER, Actor.system())
    with scope.environment(owner_environment.row_id):
        plan = plans.save(Plan(environment_id=owner_environment.row_id, title="started plan", brief="keep the service healthy", state=PlanState.STARTED, mode=PlanMode.SOLO), actor)
        phase = phases.save(Phase(environment_id=owner_environment.row_id, title="current phase", completion_rule="open work is complete"), actor)
        task = tasks.save(Task(environment_id=owner_environment.row_id, title="inspect service", brief="Inspect the service"), actor)
        links.linked(Ref.build(phase), Ref.build(plan), PHASE_TASK_LINK, actor)
        links.linked(Ref.build(task), Ref.build(phase), PHASE_LINK, actor)
        links.linked(Ref.build(task), Ref.build(plan), PLAN_LINK, actor)
        check = checks.save(Check(title="health check", brief="Read-only health check", command="true", interval=10), actor)
    app.container.get(PlanBindings).bind(plan, driver_environment.row_id, actor)
    with scope.environment(driver_environment.row_id):
        agent = agents.save(Agent(environment_id=driver_environment.row_id, session=f"observation-session-{owner_id}", provider="codex", state="leading_plan", role=AgentRole.MAIN), actor)
    plans.agent_linked(plan, agent, actor)
    template = templates.save(Template(title=f"read-only-diagnosis-{owner_id}", purpose="diagnose a failed check", brief="read only", targets=("plan",)), Actor.system())
    return {
        "authority": app.container.get(SupervisorAuthority),
        "owner": actor,
        "owner_environment": owner_environment,
        "driver_environment": driver_environment,
        "plan": plan,
        "phase": phase,
        "task": task,
        "check": check,
        "template": template,
        "credentials": [],
    }


def enrollment(fixture):
    authority = fixture["authority"]
    with app_scope(authority).environment(fixture["owner_environment"].row_id):
        context = authority.enrollment_context(fixture["plan"].row_id, (fixture["check"].row_id,), str(fixture["template"].row_id))
    return {
        "protocol_version": 1,
        "plan_id": fixture["plan"].row_id,
        "current_phase": context["current_phase"],
        "expected_plan_revision": context["expected_plan_revision"],
        "expected_binding_revision": context["expected_binding_revision"],
        "checks": [{
            "check_id": fixture["check"].row_id,
            "command_sha256": authority._command_hash(fixture["check"].command),
            "baseline_interval_minutes": 10,
            "minimum_interval_minutes": 5,
            "expected_revision": context["check_revisions"][str(fixture["check"].row_id)],
        }],
        "diagnostic_template_id": str(fixture["template"].row_id),
        "diagnostic_template_revision": context["diagnostic_template_revision"],
        "capabilities": {"diagnostic_task": True, "plan_priorities": True, "check_interval": True, "sequence": False, "phrase_nudge": False, "project_reminder": False},
        "limits": {"max_turns_per_day": 4, "max_input_tokens_per_turn": 1000, "max_output_tokens_per_turn": 1000,
            "max_provider_requests_per_turn": 8, "max_turn_seconds": 60, "max_cost_microusd_per_day": 10000,
            "max_bundles_per_project_day": 20, "max_bundles_per_episode_day": 1, "max_new_diagnostics_per_episode": 1},
        "mode": "shadow",
        "valid_until_ms": int((authority.time_source.seconds() + 3600) * 1000),
    }


def app_scope(authority):
    return authority.scope


def enrolled(fixture):
    grant, token = fixture["authority"].enroll(fixture["owner"], enrollment(fixture))
    fixture["credentials"].append(fixture["authority"]._credential_name(grant["grant_id"], grant["grant_version"]))
    return grant, token, fixture["authority"].authenticate(token)


def stored_run(app, grant, run_ref="run-observation", epoch=2, fence=7):
    scope = app.container.get(Scope)
    control = app.container.get(SupervisorEntries)
    tenant = grant["scope"]["tenant_id"]
    now = app.container.get(TimeSource).seconds()
    actor = Actor.plugin("journal-supervisor")
    with scope.environment(PROJECT):
        control.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorInstallation", actor=actor,
            data={"tenant_id": tenant, "grant_id": grant["grant_id"], "installation_id": "test-installation", "epoch": epoch},
            idempotency=f"test:installation:{tenant}"), actor)
        run = control.recorded(Entry(environment_id=PROJECT, entry_type="SupervisorRun", actor=actor,
            data={"tenant_id": tenant, "grant_id": grant["grant_id"], "grant_version": grant["grant_version"],
                "plan_id": grant["plan_id"], "node_id": grant["scope"]["writer_node_id"], "episode_id": "episode-observation",
                "installation_epoch": epoch, "fence": fence, "run_ref": run_ref,
                "lease_until": datetime.fromtimestamp(now + 300, timezone.utc).isoformat(),
                "reservation": {"cost_usd": "0.001"}, "status": "admitted"},
            idempotency=f"test:run:{tenant}:{run_ref}"), actor)
    return run


def observation_entry(app, grant, serial, epoch, committed_at_ms, output="evidence", expires_at_ms=None):
    scope_data = {**grant["scope"], "installation_epoch": epoch}
    observation_id = f"observation-{epoch}-{serial}-{uuid.uuid4().hex}"
    output_sha256 = hashlib.sha256(output.encode("utf-8")).hexdigest()
    observation = {
        "protocol_version": 1,
        "observation_id": observation_id,
        "scope": scope_data,
        "plan_id": grant["plan_id"],
        "source_ref": {"table": "checks", "id": grant["checks"][0]["check_id"]},
        "source_revision": hashlib.sha256(f"revision-{serial}".encode()).hexdigest(),
        "committed_at_ms": committed_at_ms,
        "captured_at_ms": committed_at_ms,
        "evidence_generation": serial,
        "kind": "check_completed",
        "facts": {
            "check_id": grant["checks"][0]["check_id"], "run_id": observation_id,
            "started_at_ms": committed_at_ms - 1000, "completed_at_ms": committed_at_ms,
            "verdict": "failed", "exit_status": 1,
            "command_sha256": grant["checks"][0]["command_sha256"],
            "output_excerpt": output, "output_sha256": output_sha256,
        },
    }
    expires = expires_at_ms if expires_at_ms is not None else committed_at_ms + EVIDENCE_RETENTION_MS
    data = {
        "tenant_id": scope_data["tenant_id"], "project_id": scope_data["project_id"],
        "environment_id": scope_data["environment_id"], "manager_id": scope_data["manager_id"],
        "node_id": scope_data["writer_node_id"], "installation_id": "test-installation",
        "installation_epoch": epoch, "grant_id": grant["grant_id"], "grant_version": grant["grant_version"],
        "plan_id": grant["plan_id"], "check_id": grant["checks"][0]["check_id"],
        "run_id": observation_id, "observation_id": observation_id, "evidence_generation": serial,
        "committed_at_ms": committed_at_ms, "expires_at_ms": expires,
        "retention_policy": "supervisor-check-evidence-30-days", "fault": "", "stopped": False,
        "context": {"plan_id": grant["plan_id"], "plan_state": "started"}, "observation": observation,
    }
    actor = Actor.plugin("journal-supervisor")
    with app.container.get(Scope).environment(PROJECT):
        return app.container.get(SupervisorEntries).recorded(Entry(environment_id=PROJECT,
            entry_type=OBSERVATION_ENTRY, actor=actor, data=data,
            idempotency=f"test:observation:{grant['grant_id']}:{epoch}:{serial}"), actor)


def observed(app, token, body, environment_header="untrusted-environment"):
    headers = {"Content-Type": "application/json", TOKEN_HEADER: token, "X-Journal-Env": environment_header}
    request = RequestReading.read(RequestReading.head("POST", "/_supervisor/v1/observe", headers),
        json.dumps(body).encode("utf-8"), app.container.get(Identity), app.container.get(SupervisorRequestAuth))
    return app.container.get(SupervisorController).observe(request)


def test_check_evidence_survives_latest_result_overwrite(app, supervisor_fixture, monkeypatch, tmp_path):
    fixture = supervisor_fixture
    grant, _, _ = enrolled(fixture)
    restored_run = stored_run(app, grant, run_ref="restored-observe-run", epoch=2)
    checks = app.container.get(Checks)
    runner = app.container.get(CheckRunner)
    scope = app.container.get(Scope)
    actor = Actor.plugin("check-runner")
    outputs = ("first committed result", "second committed result")
    for output in outputs:
        with scope.environment(fixture["owner_environment"].row_id):
            check = checks.find(fixture["check"].row_id)
            started = app.container.get(TimeSource).seconds()
            check = checks.rewritten(check, actor, lambda row: row.started(started, 0))
        monkeypatch.setattr(runner, "executed", lambda *args, text=output: FinishedRun(True, text))
        runner.finished(check, started, actor, object(), tmp_path / "missing-report.json")

    with scope.environment(PROJECT):
        evidence = app.container.get(Entries).supervisor_records(OBSERVATION_ENTRY, last=10, grant_id=grant["grant_id"], grant_version=grant["grant_version"])
    assert [row.data["observation"]["facts"]["output_excerpt"] for row in reversed(evidence)] == list(outputs), "each run has its own copied result after the check row is overwritten"
    assert evidence[0].data["observation"]["scope"]["environment_id"] == fixture["driver_environment"].row_id and fixture["plan"].environment_id == fixture["owner_environment"].row_id != fixture["driver_environment"].row_id, "the observation follows its credential-bound driver scope while retaining its owner-environment plan context"
    assert all(row.data["observation"]["facts"]["output_sha256"] == hashlib.sha256(row.data["observation"]["facts"]["output_excerpt"].encode()).hexdigest() for row in evidence), "the evidence hash covers its redacted copied excerpt"

    settings = app.container.get(SettingRows)
    monkeypatch.setattr(settings, "integer", lambda _: 0)
    app.container.get(RecordTrim).tick(app.container.get(TimeSource).seconds())
    backup = tmp_path / "journal-backup.db"
    app.container.get(JournalBackup).write(backup)
    restore_root = tmp_path / "restored"
    restore_config = Config(restore_root, port=0)
    restore_config.home.mkdir(parents=True)
    shutil.copyfile(backup, restore_config.database)
    (restore_config.home / "project-id").write_text(grant["scope"]["project_id"])
    restored = SuiteApp(restore_config)
    restored_scope = restored.container.get(Scope)
    with restored_scope.environment(PROJECT):
        restored_entries = restored.container.get(Entries)
        copied = restored_entries.supervisor_records(OBSERVATION_ENTRY, last=10, grant_id=grant["grant_id"], grant_version=grant["grant_version"])
        grant_row = restored_entries.selected_globally(restored_entries.query().filter(entry_type="SupervisorGrant").filter_json("data->grant_id", grant["grant_id"]).order_descending("id").limit(1))[0]
    assert [row.data["observation"]["facts"]["output_excerpt"] for row in reversed(copied)] == list(outputs), "trimmed evidence remains distinguishable in a restored journal backup"
    restored_authority = restored.container.get(SupervisorAuthority)
    monkeypatch.setattr(restored_authority.agents, "is_running", lambda _: True)
    restored_grant = restored_authority._public_grant(grant_row)
    restored_principal = restored_authority._principal(restored_grant)
    response = restored.container.get(SupervisorObservations).observe(restored_principal, {
        "protocol_version": 1, "run_id": restored_run.data["run_ref"], "installation_epoch": 2,
        "fence": restored_run.data["fence"], "cursor": None,
    })
    assert response["page"]["observation_watermark_ms"] == max(row.data["committed_at_ms"] for row in copied), "a restored observer recovers the committed watermark from copied evidence"
    assert all(row["scope"]["installation_epoch"] == 2 for row in response["page"]["observations"]), "restored pages keep the installation epoch recorded with evidence"
    restored.container.get(Connection).close()


def test_rolled_back_check_write_has_no_observation(app, supervisor_fixture):
    fixture = supervisor_fixture
    grant, _, _ = enrolled(fixture)
    checks = app.container.get(Checks)
    observations = app.container.get(SupervisorObservations)
    scope = app.container.get(Scope)
    actor = Actor.plugin("check-runner")
    with scope.environment(fixture["owner_environment"].row_id):
        check = checks.find(fixture["check"].row_id)
        started = app.container.get(TimeSource).seconds()
        result = check.started(started, 0).completed(False, "rolled-back output", app.container.get(TimeSource).moment(), 1, None, "", started)
        event = next(event for event in result.events if isinstance(event, CheckCompleted))
        with pytest.raises(RuntimeError):
            with checks.writing():
                observations.completed(check, event, started, "")
                checks.rewritten(check, actor, lambda _: result)
                raise RuntimeError("rollback check row and observation")
        stored_check = checks.find(check.row_id)
    with scope.environment(PROJECT):
        evidence = app.container.get(Entries).supervisor_records(OBSERVATION_ENTRY, last=10, grant_id=grant["grant_id"])
    assert not evidence and stored_check.last_output == "", "a rolled-back check transaction leaves neither latest output nor observation evidence"


def test_stopped_or_faulted_check_is_not_pass(app, supervisor_fixture, monkeypatch, tmp_path):
    fixture = supervisor_fixture
    grant, _, _ = enrolled(fixture)
    checks = app.container.get(Checks)
    runner = app.container.get(CheckRunner)
    scope = app.container.get(Scope)
    actor = Actor.plugin("check-runner")
    with scope.environment(fixture["owner_environment"].row_id):
        check = checks.find(fixture["check"].row_id)
        fault_start = app.container.get(TimeSource).seconds()
        check = checks.rewritten(check, actor, lambda row: row.started(fault_start, 0))
    monkeypatch.setattr(runner, "executed", lambda *_: FinishedRun(False, "missing executable", "the command is not there"))
    runner.finished(check, fault_start, actor, object(), tmp_path / "missing-report.json")

    with scope.environment(fixture["owner_environment"].row_id):
        check = checks.find(fixture["check"].row_id)
        stopped_start = app.container.get(TimeSource).seconds()
        check = checks.rewritten(check, actor, lambda row: row.started(stopped_start, 2_147_483_647))
        runner.progressed(check, stopped_start, CheckOutput.progress("partial stopped output", stopped_start), actor)
        runner.stop(check, actor)
    with scope.environment(PROJECT):
        evidence = app.container.get(Entries).supervisor_records(OBSERVATION_ENTRY, last=10, grant_id=grant["grant_id"])
    verdicts = {row.data["observation"]["facts"]["verdict"] for row in evidence}
    assert verdicts == {"faulted", "stopped"}, "faults and stops stay distinct from passed results"
    assert any(row.data["fault"] == "the command is not there" for row in evidence), "the bounded fault detail is retained"


def test_evidence_reads_are_bounded_and_redacted(app, supervisor_fixture):
    fixture = supervisor_fixture
    grant, token, _ = enrolled(fixture)
    check = fixture["check"]
    started = app.container.get(TimeSource).seconds()
    completed = app.container.get(TimeSource).seconds()
    secret = "supervisor-observation-secret-value"
    secret_name = "SUPERVISOR_OBSERVATION_TEST"
    secrets = app.container.get(SecretValues)
    secrets.put(secret_name, secret)
    event = CheckCompleted(environment_id=fixture["owner_environment"].row_id, time=completed, check_id=check.row_id,
        title=check.title, passed=False, output=("x" * 20_000) + secret, prior_failure=False,
        wait_target=False, failure_reported_at=0)
    with app.container.get(Scope).environment(fixture["owner_environment"].row_id), app.container.get(Checks).writing():
        app.container.get(SupervisorObservations).completed(check, event, started, "")
    run = stored_run(app, grant, epoch=1)
    response = observed(app, token, {"protocol_version": 1, "run_id": run.data["run_ref"], "installation_epoch": 1, "fence": 7, "cursor": None})
    excerpt = response.body["page"]["observations"][0]["facts"]["output_excerpt"]
    assert response.status == 200 and len(excerpt) <= 16_384, "the authenticated page never returns an unbounded excerpt"
    assert secret not in excerpt and f"[secret {secret_name}]" in excerpt, "the stored and returned evidence is redacted before it is hashed"
    fact = response.body["page"]["observations"][0]["facts"]
    assert fact["output_sha256"] == hashlib.sha256(excerpt.encode("utf-8")).hexdigest(), "the evidence hash is over the bounded redacted excerpt"
    secrets.drop([secret_name])


def test_cursor_recovers_all_committed_observations_after_lost_hints(app, supervisor_fixture):
    fixture = supervisor_fixture
    grant, token, _ = enrolled(fixture)
    run = stored_run(app, grant, epoch=2)
    now_ms = int(app.container.get(TimeSource).seconds() * 1000)
    observation_entry(app, grant, 1, 1, now_ms + 100_000, "restored-old-epoch")
    for serial in range(1, 102):
        observation_entry(app, grant, serial, 2, now_ms + serial, f"result-{serial}")
    body = {"protocol_version": 1, "run_id": run.data["run_ref"], "installation_epoch": 2, "fence": 7, "cursor": None}

    first = observed(app, token, body, str(fixture["owner_environment"].row_id))
    assert first.status == 200 and len(first.body["page"]["observations"]) == 100, "the authenticated cursor read is bounded to one hundred observations"
    assert first.body["snapshot"]["grant"]["scope"]["environment_id"] == fixture["driver_environment"].row_id and first.body["snapshot"]["plan_id"] == fixture["plan"].row_id, "the snapshot uses owner and driver bindings derived from the grant"
    assert first.body["snapshot"]["writable"] is False, "a shadow grant observes without reporting writable authority"
    assert first.body["page"]["next_cursor"], "a full page returns a durable cursor for the next page"
    assert all(row["scope"]["installation_epoch"] == 2 for row in first.body["page"]["observations"]), "a restored epoch does not mix older installation evidence"
    assert first.body["page"]["observation_watermark_ms"] == now_ms + 101, "the watermark covers committed evidence in the current epoch"
    second_body = {**body, "cursor": first.body["page"]["next_cursor"]}
    second = observed(app, token, second_body, str(fixture["driver_environment"].row_id))
    assert second.status == 200 and [row["facts"]["output_excerpt"] for row in second.body["page"]["observations"]] == ["result-101"], "a lost notification is recovered through the persisted cursor"
    assert second.body["page"]["cursor"] == first.body["page"]["next_cursor"], "the page echoes the caller cursor"
    assert second.body["page"]["node_heartbeat_at_ms"] > 0, "each authenticated observation response carries a node heartbeat"


def test_observe_rejects_second_tenant_run_without_rows(app, supervisor_fixture, monkeypatch):
    first_fixture = supervisor_fixture
    second_fixture = seeded(app, owner_id=2)
    monkeypatch.setattr(second_fixture["authority"].agents, "is_running", lambda _: True)
    first_grant, first_token, _ = enrolled(first_fixture)
    second_grant, _, _ = enrolled(second_fixture)
    other_run = stored_run(app, second_grant, run_ref="other-tenant-run", epoch=2)
    before = app.container.get(Entries).global_last_id()
    response = observed(app, first_token, {"protocol_version": 1, "run_id": other_run.data["run_ref"], "installation_epoch": 2, "fence": 7, "cursor": None})
    assert response.status == 403 and set(response.body) == {"error"}, "a valid grant cannot read another tenant's run"
    assert first_grant["scope"]["tenant_id"] != second_grant["scope"]["tenant_id"] and app.container.get(Entries).global_last_id() == before, "scope is derived from the credential and the rejected read changes no row"


def test_own_notes_do_not_reset_stall_or_create_feedback_episode(app, supervisor_fixture):
    fixture = supervisor_fixture
    grant, _, principal = enrolled(fixture)
    stored_run(app, grant, epoch=2)
    observations = app.container.get(SupervisorObservations)
    time_source = app.container.get(TimeSource)
    scope = app.container.get(Scope)
    check = fixture["check"]
    first_time = time_source.seconds()
    first = CheckCompleted(environment_id=fixture["owner_environment"].row_id, time=first_time,
        check_id=check.row_id, title=check.title, passed=False, output="health check still fails",
        prior_failure=False, wait_target=False, failure_reported_at=0)
    with scope.environment(fixture["owner_environment"].row_id):
        observations.completed(check, first, first_time - 1, "")
        plans = app.container.get(Plans)
        tasks = app.container.get(Tasks)
        plan = plans.find(fixture["plan"].row_id)
        actor = Actor.plugin("journal-supervisor")
        plans.save(plan.prioritised("Review the health check", grant["current_phase"]["number"], first_time), actor)
        note = tasks.save(Task(environment_id=fixture["owner_environment"].row_id, title="Read-only diagnostic",
            brief="Inspect existing evidence only"), actor)
        plans.place_task_in_phase(note, plan, fixture["phase"], actor)

    initial = observations.episode_qualification(principal, 2)
    second_time = first_time
    second = CheckCompleted(environment_id=fixture["owner_environment"].row_id, time=second_time,
        check_id=check.row_id, title=check.title, passed=False, output="health check still fails",
        prior_failure=True, wait_target=False, failure_reported_at=0)
    with scope.environment(fixture["owner_environment"].row_id):
        observations.completed(check, second, second_time - 1, "")
    repeated = observations.episode_qualification(principal, 2)
    assert initial["status"] == repeated["status"] == "actionable_stall"
    assert repeated["episode_id"] == initial["episode_id"] and repeated["progress_watermark_ms"] == initial["progress_watermark_ms"]


def test_two_attempts_escalate_once_without_further_writes(app, supervisor_fixture):
    fixture = supervisor_fixture
    grant, _, principal = enrolled(fixture)
    stored_run(app, grant, epoch=2)
    observations = app.container.get(SupervisorObservations)
    time_source = app.container.get(TimeSource)
    check = fixture["check"]
    now = time_source.seconds()
    event = CheckCompleted(environment_id=fixture["owner_environment"].row_id, time=now, check_id=check.row_id,
        title=check.title, passed=False, output="health check failed", prior_failure=False,
        wait_target=False, failure_reported_at=0)
    with app.container.get(Scope).environment(fixture["owner_environment"].row_id):
        observations.completed(check, event, now - 1, "")
    episode = observations.episode_qualification(principal, 2)
    first = observations.record_episode_attempt(principal, episode["episode_id"], "attempt-one")
    second = observations.record_episode_attempt(principal, episode["episode_id"], "attempt-two")
    with app.container.get(Scope).environment(PROJECT):
        escalations = app.container.get(Entries).supervisor_records(
            "SupervisorEpisode", last=100, tenant_id=grant["scope"]["tenant_id"],
            episode_id=episode["episode_id"], record_kind="escalation", status="needs_owner",
        )
        before = app.container.get(Entries).global_last_id()
    third = observations.record_episode_attempt(principal, episode["episode_id"], "attempt-three")
    with app.container.get(Scope).environment(PROJECT):
        after = app.container.get(Entries).global_last_id()
    assert first["attempt_count"] == 1 and first["status"] == "admitted"
    assert second["attempt_count"] == 2 and second["status"] == "needs_owner"
    assert third["status"] == "needs_owner" and third["attempt_count"] == 2
    assert len(escalations) == 1 and after == before, "the journal escalates at the attempt bound once and admits no further write"


def test_episode_qualification_separates_gates_and_busy_work_from_actionable_stalls(app):
    qualification = app.container.get(SupervisorEpisodeQualification)
    open_task = {"id": 1, "phase_id": 3, "state": "open", "delegated": False, "holder": None, "waits": []}
    context = {"plan_state": "started", "phase": {"id": 3}, "tasks": [open_task],
        "gates": {"explicit_owner_pause": False, "reserved_checkpoint": False, "ended_drive": False,
            "pending_owner_decision": False, "unpassed_phase_commands": []}, "started_task_id": None}
    cases = [
        ({**context, "plan_state": "paused", "gates": {**context["gates"], "explicit_owner_pause": True}}, "paused"),
        ({**context, "gates": {**context["gates"], "reserved_checkpoint": True}}, "owner_wait"),
        ({**context, "tasks": [{**open_task, "waits": [{"table": "tasks", "id": 2}]}]}, "external_dependency"),
        ({**context, "tasks": [{**open_task, "delegated": True}]}, "busy_worker"),
        ({**context, "started_task_id": 1}, "busy_driver"),
        (context, "actionable_stall"),
    ]
    assert [(qualification._stall_reason(candidate), expected) for candidate, expected in cases] == [
        (expected, expected) for _, expected in cases
    ]


def test_record_trim_retains_protected_receipts_and_evidence(app, supervisor_fixture, monkeypatch):
    fixture = supervisor_fixture
    grant, _, _ = enrolled(fixture)
    now_ms = int(app.container.get(TimeSource).seconds() * 1000)
    evidence = observation_entry(app, grant, 1, 1, now_ms, "unexpired evidence")
    expired = observation_entry(app, grant, 2, 1, now_ms, "expired evidence", now_ms - 1)
    actor = Actor.plugin("journal-supervisor")
    with app.container.get(Scope).environment(PROJECT):
        receipt = app.container.get(SupervisorEntries).recorded(Entry(environment_id=PROJECT,
            entry_type="SupervisorActionReceipt", actor=actor, data={"tenant_id": grant["scope"]["tenant_id"], "action_id": "receipt-1", "status": "complete"},
            idempotency="test:receipt:1"), actor)
        ordinary = app.container.get(Entries).recorded(Entry(environment_id=PROJECT, entry_type="ordinary", actor=fixture["owner"], data={"detail": "trim me"}, idempotency="test:ordinary"), fixture["owner"])
    settings = app.container.get(SettingRows)
    monkeypatch.setattr(settings, "integer", lambda _: 0)
    app.container.get(RecordTrim).tick(app.container.get(TimeSource).seconds())
    with app.container.get(Scope).environment(PROJECT):
        entries = app.container.get(Entries)
        retained_evidence = entries.supervisor_records(OBSERVATION_ENTRY, last=1, observation_id=evidence.data["observation_id"])
        erased_evidence = entries.supervisor_records(OBSERVATION_ENTRY, last=1, observation_id=expired.data["observation_id"])
        retained_receipt = entries.supervisor_records("SupervisorActionReceipt", last=1, action_id="receipt-1")
        ordinary_rows = entries.selected_globally(entries.query().filter(id=ordinary.row_id).limit(1))
    assert retained_evidence and retained_receipt and not erased_evidence, "normal trimming preserves protected receipts and unexpired evidence while the explicit retention pass erases expired evidence"
    assert not ordinary_rows, "ordinary records still follow the configured trim limit"
