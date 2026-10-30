import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request as HttpRequest, urlopen

import pytest

from journal.config import Config
from journal.http.support.identity import Identity
from journal.http.router import Router
from journal.http.support.request_reading import RequestReading
from journal.http.support.supervisor_authentication import SupervisorRequestAuth
from journal.features.plans.support.plan_bindings import PlanBindings
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.agent import Agent
from journal.models.check import Check
from journal.models.entry import Entry
from journal.models.environment import Environment
from journal.models.link import Link
from journal.models.phase import Phase
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.template import Template
from journal.models.user import User
from journal.repositories.agents import Agents
from journal.repositories.checks import Checks
from journal.repositories.entries import Entries
from journal.repositories.environment_owners import OWNER
from journal.repositories.environments import Environments
from journal.repositories.links import Links
from journal.repositories.phases import PHASE_TASK_LINK, Phases
from journal.repositories.plans import PHASE_LINK, PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.repositories.tasks import Tasks
from journal.repositories.templates import Templates
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.support.rejection import Rejection
from journal.supervisor_authority import GRANT_ENTRY, GRANT_FIELDS, RESERVED_OPERATIONS, SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from tests.suite_app import SuiteApp


@dataclass
class Fixture:
    authority: SupervisorAuthority
    owner: Actor
    owner_environment: Environment
    driver_environment: Environment
    plan: Plan
    phase: Phase
    task: Task
    agent: Agent
    check: Check
    template: Template
    credentials: list[str] = field(default_factory=list)


@pytest.fixture(scope="module")
def boot():
    def booted(root, patch):
        return SuiteApp(Config(root, port=0))
    return booted


def seeded(app, owner_id: int = 1) -> Fixture:
    actor = Actor.user(owner_id)
    scope = app.container.get(Scope)
    environments = app.container.get(Environments)
    links = app.container.get(Links)
    plans = app.container.get(Plans)
    tasks = app.container.get(Tasks)
    phases = app.container.get(Phases)
    agents = app.container.get(Agents)
    checks = app.container.get(Checks)
    templates = app.container.get(Templates)

    owner_environment = environments.made(f"supervisor-owner-{owner_id}", actor)
    driver_environment = environments.made(f"supervisor-driver-{owner_id}", actor)
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
    bindings = app.container.get(PlanBindings)
    bindings.bind(plan, driver_environment.row_id, actor)
    with scope.environment(driver_environment.row_id):
        agent = agents.save(Agent(environment_id=driver_environment.row_id, session=f"supervisor-session-{owner_id}", provider="codex", state="leading_plan", role=AgentRole.MAIN), actor)
    plans.agent_linked(plan, agent, actor)
    template = templates.save(Template(title=f"read-only-check-diagnosis-{owner_id}", purpose="diagnose a failed check", brief="read only", targets=("plan",)), Actor.system())
    authority = app.container.get(SupervisorAuthority)
    return Fixture(authority, actor, owner_environment, driver_environment, plan, phase, task, agent, check, template)


@pytest.fixture
def authority_fixture(app, monkeypatch):
    fixture = seeded(app)
    monkeypatch.setattr(fixture.authority.agents, "is_running", lambda environment: True)
    yield fixture
    fixture.authority.secrets_store.drop(fixture.credentials)


def enrollment(fixture: Fixture, mode: str = "shadow") -> dict:
    authority = fixture.authority
    context = authority.enrollment_context(fixture.plan.row_id, (fixture.check.row_id,), str(fixture.template.row_id))
    return {
        "protocol_version": 1,
        "plan_id": fixture.plan.row_id,
        "current_phase": context["current_phase"],
        "expected_plan_revision": context["expected_plan_revision"],
        "expected_binding_revision": context["expected_binding_revision"],
        "checks": [{
            "check_id": fixture.check.row_id,
            "command_sha256": authority._command_hash(fixture.check.command),
            "baseline_interval_minutes": 10,
            "minimum_interval_minutes": 5,
            "expected_revision": context["check_revisions"][str(fixture.check.row_id)],
        }],
        "diagnostic_template_id": str(fixture.template.row_id),
        "diagnostic_template_revision": context["diagnostic_template_revision"],
        "capabilities": {"diagnostic_task": True, "plan_priorities": True, "check_interval": True, "sequence": False, "phrase_nudge": False, "project_reminder": False},
        "limits": {"max_turns_per_day": 4, "max_input_tokens_per_turn": 1000, "max_output_tokens_per_turn": 1000,
            "max_provider_requests_per_turn": 8, "max_turn_seconds": 60, "max_cost_microusd_per_day": 10000,
            "max_bundles_per_project_day": 20, "max_bundles_per_episode_day": 1, "max_new_diagnostics_per_episode": 1},
        "mode": mode,
        "valid_until_ms": int((authority.time_source.seconds() + 3600) * 1000),
    }


def admitted(fixture: Fixture, mode: str = "shadow"):
    grant, token = fixture.authority.enroll(fixture.owner, enrollment(fixture, mode))
    fixture.credentials.append(fixture.authority._credential_name(grant["grant_id"], grant["grant_version"]))
    return grant, token, fixture.authority.authenticate(token)


def grant_rows(entries: Entries) -> int:
    return len(entries.selected_globally(entries.query().filter(entry_type=GRANT_ENTRY)))


def test_bad_service_credentials_never_fall_back_to_local_person(app, authority_fixture, monkeypatch):
    fixture = authority_fixture
    identity = app.container.get(Identity)
    monkeypatch.setattr(identity, "build", lambda *_: pytest.fail("supervisor auth must decide before local-person fallback"))
    auth = app.container.get(SupervisorRequestAuth)
    before = app.container.get(Entries).global_last_id()
    secrets_before = fixture.authority.secrets_store.values()

    missing = RequestReading.read(RequestReading.head("POST", "/_supervisor/v1/admit", {"Content-Type": "application/json"}), b'{"plan_id":1}', identity, auth)
    invalid = RequestReading.read(RequestReading.head("POST", "/_supervisor/v1/receipt", {"Content-Type": "application/json", "X-Journal-Supervisor-Token": "wrong"}), b'{"receipt_id":"private"}', identity, auth)
    generic = RequestReading.read(RequestReading.head("POST", "/cli", {"Content-Type": "application/json", "X-Journal-Supervisor-Token": "wrong"}), b'{"argv":["settings"]}', identity, auth)
    owner_without_session = RequestReading.read(RequestReading.head("POST", "/_supervisor/v1/enrollment", {"Content-Type": "application/json"}), b'{"protocol_version":1}', identity, auth)

    assert (missing.auth_error.status, invalid.auth_error.status, generic.auth_error.status, owner_without_session.auth_error.status) == (401, 403, 403, 401), "missing, invalid and generic-route service credentials and owner routes without browser sessions fail before identity fallback"
    assert missing.body == invalid.body == generic.body == owner_without_session.body == {}, "rejected requests do not parse or return row/evidence payloads"
    assert all(set(request.auth_error.body) == {"error"} for request in (missing, invalid, generic, owner_without_session)), "rejections reveal no grant, row or evidence fields"
    assert app.container.get(Entries).global_last_id() == before, "rejected credentials do not mutate the Entry log"
    assert fixture.authority.secrets_store.values() == secrets_before, "rejected service credentials do not rotate or alter stored credentials"

    grant, revoked_token = fixture.authority.enroll(fixture.owner, enrollment(fixture))
    fixture.credentials.append(fixture.authority._credential_name(grant["grant_id"], grant["grant_version"]))
    fixture.authority.change(fixture.owner, {"protocol_version": 1, "grant_id": grant["grant_id"], "expected_grant_version": 1, "change": {"kind": "revoke"}})
    revoked_before = app.container.get(Entries).global_last_id()
    revoked_secrets = fixture.authority.secrets_store.values()
    revoked = RequestReading.read(RequestReading.head("POST", "/_supervisor/v1/apply", {"Content-Type": "application/json", "X-Journal-Supervisor-Token": revoked_token}), b'{"action_id":"private"}', identity, auth)
    assert revoked.auth_error.status == 403 and revoked.body == {} and set(revoked.auth_error.body) == {"error"}, "a revoked credential fails before local-person fallback and reveals no evidence"
    assert app.container.get(Entries).global_last_id() == revoked_before and fixture.authority.secrets_store.values() == revoked_secrets, "a revoked request changes no Entry or stored credential"
    mismatched = RequestReading.read(RequestReading.head("POST", "/_supervisor/v1/enrollment", {"Content-Type": "application/json", "X-Journal-Supervisor-Token": revoked_token}), b'{"protocol_version":1}', identity, auth)
    assert mismatched.auth_error.status == 403 and mismatched.body == {}, "a service credential cannot enter the owner route or fall back to a local person"


def test_only_actual_owner_can_enroll_or_revoke(app, authority_fixture, monkeypatch):
    fixture = authority_fixture
    body = enrollment(fixture)
    entries = app.container.get(Entries)
    before = grant_rows(entries)
    secrets_before = fixture.authority.secrets_store.values()

    for actor in (Actor.user(2), Actor.agent("agent-session"), Actor.plugin("untrusted-plugin")):
        with pytest.raises(SupervisorFailure) as denied:
            fixture.authority.enroll(actor, body)
        assert denied.value.status == 403
    assert grant_rows(entries) == before, "a colleague, agent or plugin cannot create a grant"
    assert fixture.authority.secrets_store.values() == secrets_before, "rejected owner enrollment does not alter stored credentials"

    auth = app.container.get(SupervisorRequestAuth)
    identity = app.container.get(Identity)
    session_person = fixture.owner.number()
    monkeypatch.setattr(auth.sessions, "session", lambda cookie: SimpleNamespace(person=session_person) if cookie == "browser=owner" else None)

    def owner_request(request_body):
        head = RequestReading.head("POST", "/_supervisor/v1/enrollment", {"Content-Type": "application/json", "Cookie": "browser=owner"})
        return RequestReading.read(head, json.dumps(request_body).encode(), identity, auth)

    before_non_owner_route = grant_rows(entries)
    non_owner_secrets = fixture.authority.secrets_store.values()
    session_person = 2
    non_owner_response = app.container.get(Router).route(owner_request(body))
    assert non_owner_response.status == 403 and grant_rows(entries) == before_non_owner_route and fixture.authority.secrets_store.values() == non_owner_secrets, "an authenticated colleague cannot enroll or change stored credentials through the management route"
    session_person = fixture.owner.number()
    response = app.container.get(Router).route(owner_request(body))
    assert response.status == 201 and response.headers.get("Cache-Control") == "no-store", "the owner-only HTTP route creates a grant privately"
    grant = response.body
    token = response.headers["X-Journal-Supervisor-Token"]
    fixture.credentials.append(fixture.authority._credential_name(grant["grant_id"], grant["grant_version"]))
    assert set(grant) == GRANT_FIELDS, "the Entry grant and owner response use the frozen closed Grant shape"
    assert "token" not in grant and "credential" not in grant, "the service credential is returned once in a no-store header, never in the grant body"
    change = {"protocol_version": 1, "grant_id": grant["grant_id"], "expected_grant_version": 1, "change": {"kind": "revoke"}}
    with pytest.raises(SupervisorFailure) as denied:
        fixture.authority.change(Actor.user(2), change)
    assert denied.value.status == 403 and grant_rows(entries) == before + 1, "only the recorded plan owner can revoke"

    rotate = {"protocol_version": 1, "grant_id": grant["grant_id"], "expected_grant_version": 1,
        "change": {"kind": "replace", "enrollment": enrollment(fixture, "bounded_write")}}
    def owner_change(request_body):
        head = RequestReading.head("POST", "/_supervisor/v1/enrollment/change", {"Content-Type": "application/json", "Cookie": "browser=owner"})
        return RequestReading.read(head, json.dumps(request_body).encode(), identity, auth)

    rotated_response = app.container.get(Router).route(owner_change(rotate))
    grant, replacement_token = rotated_response.body, rotated_response.headers["X-Journal-Supervisor-Token"]
    fixture.credentials.append(fixture.authority._credential_name(grant["grant_id"], grant["grant_version"]))
    assert grant["grant_version"] == 2 and grant["mode"] == "bounded_write" and replacement_token != token, "revision increments the grant and rotates the service credential"
    with pytest.raises(SupervisorFailure):
        fixture.authority.authenticate(token)
    fixture.authority.authenticate(replacement_token)

    change = {"protocol_version": 1, "grant_id": grant["grant_id"], "expected_grant_version": 2, "change": {"kind": "revoke"}}
    before_revoke = grant_rows(entries)
    with pytest.raises(SupervisorFailure) as denied:
        fixture.authority.change(Actor.user(2), change)
    assert denied.value.status == 403 and grant_rows(entries) == before_revoke, "a colleague cannot revoke a rotated grant"
    change_response = app.container.get(Router).route(owner_change(change))
    revoked, raw_token = change_response.body, change_response.headers.get("X-Journal-Supervisor-Token")
    assert revoked["grant_version"] == 3 and revoked["revoked"] and revoked["mode"] == "disabled" and raw_token is None
    assert app.container.get(Plans).find(fixture.plan.row_id).state == PlanState.STARTED, "enrollment and revocation do not approve, start, pause or resume a plan"
    with app.container.get(Scope).environment(fixture.driver_environment.row_id):
        assert app.container.get(Agents).find(fixture.agent.row_id).state == "leading_plan", "enrollment and revocation do not start or resume the plan agent"
    with pytest.raises(SupervisorFailure):
        fixture.authority.authenticate(replacement_token)

    links = app.container.get(Links)
    for environment in (fixture.owner_environment, fixture.driver_environment):
        for owner_link in links.matching(target=Ref.build(environment), link_type=OWNER):
            links.delete(owner_link, Actor.system())
    before_unowned = grant_rows(entries)
    secrets_before = fixture.authority.secrets_store.values()
    with pytest.raises(SupervisorFailure) as unowned:
        fixture.authority.enroll(fixture.owner, body)
    assert unowned.value.status == 403 and grant_rows(entries) == before_unowned, "an unowned plan cannot be enrolled by a former local person"
    assert fixture.authority.secrets_store.values() == secrets_before, "unowned enrollment cannot change credential storage"


def test_scope_is_derived_from_credential(app, authority_fixture):
    fixture = authority_fixture
    other_tenant = seeded(app, 2)
    grant, token, principal = admitted(fixture)
    assert principal.scope["tenant_id"] == "owner:1"
    assert principal.scope["environment_id"] == fixture.driver_environment.row_id != fixture.owner_environment.row_id, "scope follows the owner and bound plan-agent environment"
    assert principal.scope["manager_id"] == "openclaw" and principal.scope["writer_node_id"] == principal.scope["project_id"] and principal.scope["installation_epoch"] == 1

    request = RequestReading.read(RequestReading.head("POST", "/_supervisor/v1/observe", {
        "Content-Type": "application/json", "X-Journal-Supervisor-Token": token,
        "X-Journal-Env": other_tenant.owner_environment.name, "X-Journal-Tenant": "owner:2",
    }), b'{"plan_id":1}', app.container.get(Identity), app.container.get(SupervisorRequestAuth))
    assert request.supervisor.scope == grant["scope"] == principal.scope, "caller tenant and environment headers cannot change credential scope"
    assert request.actor == Actor.plugin("journal-supervisor"), "a valid machine request is attributed as a service/plugin, not a user"
    identity = app.container.get(Identity)
    for path in ("/cli", "/shell/run", "/journal/settings"):
        blocked = RequestReading.read(RequestReading.head("POST", path, {"Content-Type": "application/json", "X-Journal-Supervisor-Token": token}), b'{"command":"settings"}', identity, app.container.get(SupervisorRequestAuth))
        assert blocked.auth_error.status == 403 and blocked.body == {}, f"a valid service credential cannot use generic route {path}"

    entries = app.container.get(Entries)
    before = entries.global_last_id()
    with pytest.raises(SupervisorFailure) as denied:
        fixture.authority.revalidate(principal, plan_id=other_tenant.plan.row_id)
    assert denied.value.status == 403 and str(other_tenant.plan.row_id) not in str(denied.value) and entries.global_last_id() == before, "a second-tenant plan reference returns no evidence and changes no row"


def test_current_phase_and_reserved_gates_are_rechecked(app, authority_fixture, monkeypatch):
    fixture = authority_fixture
    _, _, principal = admitted(fixture)
    scope = app.container.get(Scope)
    plans = app.container.get(Plans)
    tasks, phases, links = app.container.get(Tasks), app.container.get(Phases), app.container.get(Links)
    actor = fixture.owner
    entries = app.container.get(Entries)
    phase_testing = fixture.authority.phase_testing
    original_unpassed = phase_testing.unpassed

    checks = app.container.get(Checks)
    check = checks.find(fixture.check.row_id)
    checks.save(check.with_(interval=7), actor)
    fixture.authority.revalidate(principal)
    checks.save(check.with_(interval=4), actor)
    with pytest.raises(SupervisorFailure) as out_of_range:
        fixture.authority.revalidate(principal)
    assert out_of_range.value.status == 403, "the enrolled check interval can move only within its recorded range"
    checks.save(check.with_(interval=10), actor)

    with scope.environment(fixture.owner_environment.row_id):
        plans.touch(plans.find(fixture.plan.row_id), actor, state=PlanState.PAUSED)
    with pytest.raises(SupervisorFailure) as paused:
        fixture.authority.revalidate(principal)
    assert paused.value.status == 409, "a paused plan fails the live plan-state gate"
    with scope.environment(fixture.owner_environment.row_id):
        plans.touch(plans.find(fixture.plan.row_id), actor, state=PlanState.STARTED)
    fixture.authority.revalidate(principal)

    with scope.environment(fixture.owner_environment.row_id):
        second_phase = phases.save(Phase(environment_id=fixture.owner_environment.row_id, title="next phase"), actor)
        second_task = tasks.save(Task(environment_id=fixture.owner_environment.row_id, title="next work", brief="continue"), actor)
        links.linked(Ref.build(second_phase), Ref.build(fixture.plan), PHASE_TASK_LINK, actor)
        links.linked(Ref.build(second_task), Ref.build(second_phase), PHASE_LINK, actor)
        links.linked(Ref.build(second_task), Ref.build(fixture.plan), PLAN_LINK, actor)
        first_task = tasks.find(fixture.task.row_id)
        tasks.touch(first_task, actor, state=TaskState.COMPLETED, completed_at=datetime.now(timezone.utc))

    before_revalidation = grant_rows(entries)
    with pytest.raises(SupervisorFailure) as phase_changed:
        fixture.authority.revalidate(principal)
    assert phase_changed.value.status == 403 and grant_rows(entries) == before_revalidation, "an admitted credential cannot cross into a different current phase or append evidence"

    next_grant, _, next_principal = admitted(fixture)
    assert app.container.get(SettingRows).option(TasksOptions.AUTO) is True, "the hard checkpoint gate is exercised while ordinary task auto mode is on"
    with scope.environment(fixture.owner_environment.row_id):
        first_phase = phases.find(fixture.phase.row_id)
        phases.save(first_phase.with_(checkpoint=True), actor)
    with pytest.raises(SupervisorFailure) as checkpoint:
        fixture.authority.revalidate(next_principal)
    assert checkpoint.value.status == 409 and next_grant["current_phase"]["phase_id"] == second_phase.row_id, "reserved checkpoint gates are checked even when the plan is already started"

    with scope.environment(fixture.owner_environment.row_id):
        phases.save(phases.find(fixture.phase.row_id).with_(checkpoint=False), actor)
    _, _, testing_principal = admitted(fixture)
    monkeypatch.setattr(fixture.authority.phase_testing, "unpassed", lambda plan: ("pytest",))
    with pytest.raises(SupervisorFailure) as testing:
        fixture.authority.revalidate(testing_principal)
    assert testing.value.status == 409, "an unpassed phase test is a hard gate on every revalidation"

    monkeypatch.setattr(phase_testing, "unpassed", original_unpassed)
    app.container.get(PlanBindings).end(fixture.plan, "driver binding ended", actor)
    before_ended_binding = grant_rows(entries)
    with pytest.raises(SupervisorFailure) as ended:
        fixture.authority.revalidate(testing_principal)
    assert ended.value.status == 409 and grant_rows(entries) == before_ended_binding, "an ended plan-agent binding stops an admitted request without appending evidence"


def test_shadow_and_optional_capabilities_deny_domain_writes(app, authority_fixture):
    fixture = authority_fixture
    shadow, _, _ = admitted(fixture, "shadow")
    assert fixture.authority.permits_proposal_receipt(shadow), "shadow permits an explicitly validated proposal receipt"
    for operation in ("diagnostic_task", "plan_priorities", "check_interval", "sequence", "phrase_nudge", "project_reminder", *RESERVED_OPERATIONS):
        assert not fixture.authority.permits_domain_write(shadow, operation), f"shadow cannot apply {operation}"

    bounded, _, _ = admitted(fixture, "bounded_write")
    for operation in ("diagnostic_task", "plan_priorities", "check_interval"):
        assert fixture.authority.permits_domain_write(bounded, operation), f"an owner grant can narrowly permit {operation}"
    for operation in ("sequence", "phrase_nudge", "project_reminder", *RESERVED_OPERATIONS, "shell", "settings"):
        assert not fixture.authority.permits_domain_write(bounded, operation), f"optional and reserved capability {operation} stays denied"


def test_revocation_after_admission_stops_apply(app, authority_fixture, monkeypatch):
    fixture = authority_fixture
    grant, token, admitted_principal = admitted(fixture, "bounded_write")
    change = {"protocol_version": 1, "grant_id": grant["grant_id"], "expected_grant_version": 1, "change": {"kind": "revoke"}}
    fixture.authority.change(fixture.owner, change)

    with pytest.raises(SupervisorFailure) as revoked:
        fixture.authority.revalidate(admitted_principal, plan_id=fixture.plan.row_id)
    assert revoked.value.status == 403, "a principal admitted before revocation cannot pass the apply-time grant check"

    identity = app.container.get(Identity)
    monkeypatch.setattr(identity, "build", lambda *_: pytest.fail("revoked service credentials must fail before identity fallback"))
    request = RequestReading.read(RequestReading.head("POST", "/_supervisor/v1/apply", {"Content-Type": "application/json", "X-Journal-Supervisor-Token": token}), b'{"action_id":"private"}', identity, app.container.get(SupervisorRequestAuth))
    assert request.auth_error.status == 403 and request.body == {}, "revocation blocks a later apply request before any receipt/evidence is returned"


def test_generic_entry_writes_cannot_forge_grants_or_receipts(app, authority_fixture):
    fixture = authority_fixture
    grant, _ = fixture.authority.enroll(fixture.owner, enrollment(fixture))
    fixture.credentials.append(fixture.authority._credential_name(grant["grant_id"], grant["grant_version"]))
    entries = app.container.get(Entries)
    before = grant_rows(entries)
    before_log = entries.global_last_id()
    for kind in ("SupervisorGrant", "SupervisorReceipt", "SupervisorProposalReceipt"):
        with pytest.raises(Rejection):
            entries.recorded(Entry(environment_id=fixture.driver_environment.row_id, entry_type=kind, actor=Actor.plugin("agent"), data={"revoked": False}, idempotency=f"forged:{kind}"), Actor.plugin("agent"))
        with pytest.raises(Rejection):
            entries.save(Entry(environment_id=fixture.driver_environment.row_id, entry_type=kind, actor=Actor.user(1), data={}, idempotency=f"crud:{kind}"), Actor.user(1))
    assert grant_rows(entries) == before, "generic Entry appends cannot forge supervisor grants or receipts"
    assert entries.global_last_id() == before_log, "generic Entry appends cannot mutate any Entry row"

    grant_entry = entries.selected_globally(entries.query().filter(entry_type=GRANT_ENTRY).limit(1))[0]
    before_crud = entries.global_last_id()
    disguised = grant_entry.with_(entry_type="PromptSubmitted")
    with pytest.raises(Rejection):
        entries.save(disguised.with_(data={**grant_entry.data, "revoked": True}), Actor.user(1))
    with pytest.raises(Rejection):
        entries.touch(disguised, Actor.user(1), data={**grant_entry.data, "revoked": True})
    with pytest.raises(Rejection):
        entries.delete(disguised, Actor.plugin("agent"))
    assert entries.global_last_id() == before_crud, "generic Entry updates and deletion cannot replace or remove a protected grant"

    with app.container.get(Scope).environment(fixture.driver_environment.row_id):
        receipt = app.container.get(SupervisorEntries).recorded(Entry(environment_id=fixture.driver_environment.row_id, entry_type="SupervisorProposalReceipt", actor=Actor.plugin("journal-supervisor"), data={"validated": True}, idempotency="checked:proposal-receipt"), Actor.plugin("journal-supervisor"))
        entries.trim(entries.last_id(), 0)
        preserved = entries.selected(entries.query().filter(id=receipt.row_id))
    assert [row.row_id for row in preserved] == [receipt.row_id], "trim retains protected receipt kinds outside the current explicit type list"


def test_authenticated_bridge_admits_applies_and_reads_receipt_over_http(app, authority_fixture):
    from journal.events.rows.check_completed import CheckCompleted
    from journal.features.supervisor.support.supervisor_observations import SupervisorObservations
    from journal.http.server import Server
    from journal.support.time_source import TimeSource

    fixture = authority_fixture
    grant, token, principal = admitted(fixture, "bounded_write")
    observations = app.container.get(SupervisorObservations)
    time_source = app.container.get(TimeSource)
    check = app.container.get(Checks).find(fixture.check.row_id)
    observed_at = time_source.seconds()
    observations.completed(check, CheckCompleted(
        environment_id=fixture.owner_environment.row_id,
        time=observed_at,
        check_id=check.row_id,
        title=check.title,
        passed=False,
        output="health check failed",
        prior_failure=False,
        wait_target=False,
        failure_reported_at=0,
    ), observed_at - 1, "")

    server = app.container.call(Server)
    server.start()
    try:
        status, admitted_body = _post_supervisor_http(server.port, "/_supervisor/v1/admit", {
            "protocol_version": 1, "source": "timer", "observation_cursor": None,
        }, token)
        assert status == 200 and admitted_body["status"] == "admitted", admitted_body
        run = admitted_body["run"]
        assert run["grant_id"] == grant["grant_id"] and run["grant_version"] == grant["grant_version"]

        status, observed_body = _post_supervisor_http(server.port, "/_supervisor/v1/observe", {
            "protocol_version": 1,
            "run_id": run["run_id"],
            "installation_epoch": run["installation_epoch"],
            "fence": run["fence"],
            "cursor": None,
        }, token)
        assert status == 200, observed_body
        snapshot = observed_body["snapshot"]
        evidence = observed_body["page"]["observations"][0]

        with app.container.get(Scope).environment(PROJECT):
            app.container.get(SupervisorEntries).recorded(Entry(
                environment_id=PROJECT,
                entry_type="SupervisorUsage",
                actor=principal.actor,
                data={"tenant_id": principal.scope["tenant_id"], "run_ref": run["run_id"],
                    "status": "known", "turns": 1, "input_tokens": 10, "output_tokens": 10,
                    "cost_usd": "0.000001", "overrun": False},
                idempotency=f"supervisor:http-usage:{run['run_id']}",
            ), principal.actor)

        action = {
            "protocol_version": 1,
            "run_id": run["run_id"],
            "installation_epoch": run["installation_epoch"],
            "fence": run["fence"],
            "grant_version": grant["grant_version"],
            "episode_id": run["episode_id"],
            "action_id": run["pending_action_id"],
            "observation_ids": [evidence["observation_id"]],
            "expected_revisions": [
                {"ref": {"table": "plans", "id": grant["plan_id"]}, "revision": snapshot["plan_revision"]},
                {"ref": {"table": "phases", "id": snapshot["phase"]["id"]}, "revision": snapshot["phase"]["revision"]},
            ],
            "operations": [{"kind": "plan_priorities", "plan_id": grant["plan_id"], "text": "Investigate the failed check"}],
            "rationale": "Record a bounded diagnostic priority.",
        }
        status, applied = _post_supervisor_http(server.port, "/_supervisor/v1/apply", action, token)
        assert status == 200 and applied["status"] == "applied", applied

        status, receipt = _post_supervisor_http(server.port, "/_supervisor/v1/receipt", {
            "protocol_version": 1, "action_id": action["action_id"],
        }, token)
        assert status == 200 and receipt["status"] == "applied", receipt
        assert receipt["receipt_id"] == applied["receipt_id"]
        assert receipt["data"]["action_id"] == action["action_id"]
        assert receipt["data"]["verification"] == "verified"
    finally:
        server.stop()


def test_bad_bridge_credential_over_http_changes_nothing(app, authority_fixture, monkeypatch):
    from journal.http.server import Server

    fixture = authority_fixture
    admitted(fixture, "bounded_write")
    entries = app.container.get(Entries)
    before = entries.global_last_id()
    monkeypatch.setattr(app.container.get(Identity), "build", lambda *_: pytest.fail("bridge auth must reject before local-person fallback"))
    with app.container.get(Scope).environment(fixture.owner_environment.row_id):
        before_priorities = app.container.get(Plans).find(fixture.plan.row_id).priorities
    server = app.container.call(Server)
    server.start()
    try:
        status, body = _post_supervisor_http(server.port, "/_supervisor/v1/admit", {
            "protocol_version": 1, "source": "timer", "observation_cursor": None,
        }, "invalid-service-token")
    finally:
        server.stop()
    assert status == 403 and set(body) == {"error"}, body
    assert entries.global_last_id() == before, "bad bridge credentials cannot read or append supervisor rows"
    with app.container.get(Scope).environment(fixture.owner_environment.row_id):
        assert app.container.get(Plans).find(fixture.plan.row_id).priorities == before_priorities


def _post_supervisor_http(port: int, path: str, body: dict, token: str) -> tuple[int, dict]:
    request = HttpRequest(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except HTTPError as response:
        return response.code, json.loads(response.read())
