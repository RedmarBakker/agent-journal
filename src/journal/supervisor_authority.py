import hashlib
import hmac
import json
import re
import secrets
import uuid
from datetime import datetime
from typing import Any

from journal.features.plans.support.phase_testing import PhaseTesting
from journal.features.plans.support.plan_agents import PlanAgents
from journal.features.plans.support.plan_bindings import ENDED_LINK, PlanBindings
from journal.features.plans.support.plan_owners import PlanOwners
from journal.models.agent import Agent
from journal.models.check import Check
from journal.models.entry import Entry
from journal.models.link import Link
from journal.models.phase import Phase
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.support.ref import Ref
from journal.models.template import Template
from journal.repositories.checks import Checks
from journal.repositories.entries import Entries
from journal.repositories.links import Links
from journal.repositories.plans import PHASE_LINK, PHASE_TASK_LINK, PLAN_AGENT_LINK, PLAN_LINK, Plans
from journal.repositories.scope import BOUND_LINK, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.repositories.templates import Templates
from journal.support.actor import Actor
from journal.support.actor_type import ActorType
from journal.support.secret_values import SecretValues
from journal.support.time_source import TimeSource
from journal.supervisor_failure import SupervisorFailure
from journal.supervisor_principal import SupervisorPrincipal

GRANT_ENTRY = "SupervisorGrant"
SUPERVISOR_ACTOR = "journal-supervisor"
MANAGER_ID = "openclaw"
INSTALLATION_EPOCH = 1
GRANT_FIELDS = frozenset({
    "protocol_version", "grant_id", "grant_version", "owner_user_id", "scope", "plan_id",
    "driver_agent_id", "driver_environment_id", "driver_provider", "current_phase", "checks",
    "diagnostic_template_id", "diagnostic_template_revision", "capabilities", "limits", "mode",
    "valid_until_ms", "revoked",
})
CAPABILITY_FIELDS = frozenset({"diagnostic_task", "plan_priorities", "check_interval", "sequence", "phrase_nudge", "project_reminder"})
BUDGET_FIELDS = frozenset({
    "max_turns_per_day", "max_input_tokens_per_turn", "max_output_tokens_per_turn",
    "max_provider_requests_per_turn", "max_turn_seconds", "max_cost_microusd_per_day",
    "max_bundles_per_project_day", "max_bundles_per_episode_day", "max_new_diagnostics_per_episode",
})
CHECK_FIELDS = frozenset({"check_id", "command_sha256", "baseline_interval_minutes", "minimum_interval_minutes", "expected_revision"})
RESERVED_OPERATIONS = frozenset({
    "approve", "approvals", "approve_plan", "start", "start_plan", "resume", "resume_plan", "pause", "checkpoint",
    "cancel", "finish", "complete", "assign", "delegate", "sequence", "phrase_nudge", "project_reminder",
    "goal", "goals", "acceptance", "acceptance_criteria", "settings", "setting", "cli", "shell", "command",
    "cap", "caps", "capabilities", "credential", "credentials", "grant", "enrollment", "model", "models",
    "tool", "tools", "install", "installation", "upgrade", "upgrades", "release", "deploy", "deployment",
    "merge", "message", "external_message", "external_messages", "purchase", "destroy",
})
SUPPORTED_OPERATIONS = {
    "diagnostic_task": "diagnostic_task",
    "plan_priorities": "plan_priorities",
    "check_interval": "check_interval",
}


class SupervisorAuthority:
    """The checked owner and service boundary for the version 1 supervisor grant."""

    def __init__(self, entries: Entries, control_entries: SupervisorEntries, plans: Plans, owners: PlanOwners,
                 bindings: PlanBindings, agents: PlanAgents, phase_testing: PhaseTesting, checks: Checks,
                 templates: Templates, links: Links, scope: Scope, secrets_store: SecretValues,
                 time_source: TimeSource) -> None:
        self.entries, self.control_entries, self.plans = entries, control_entries, plans
        self.owners, self.bindings, self.agents, self.phase_testing = owners, bindings, agents, phase_testing
        self.checks, self.templates, self.links, self.scope = checks, templates, links, scope
        self.secrets_store, self.time_source = secrets_store, time_source

    def enrollment_context(self, plan_id: int, check_ids: tuple[int, ...] = (), template_id: str = "") -> dict[str, Any]:
        plan = self._plan(plan_id)
        context = self._eligible(plan, self.owners.number(plan))
        checks = {str(check_id): self._check_revision(self._check(check_id)) for check_id in check_ids}
        template_revision = self._template_revision(template_id) if template_id else ""
        return {
            "current_phase": context["current_phase"],
            "expected_plan_revision": context["plan_revision"],
            "expected_binding_revision": context["binding_revision"],
            "check_revisions": checks,
            "diagnostic_template_revision": template_revision,
        }

    def enroll(self, actor: Actor, body: object) -> tuple[dict[str, Any], str]:
        request = self._enrollment(body)
        grant_id, token = uuid.uuid4().hex, secrets.token_urlsafe(32)
        credential_name = self._credential_name(grant_id, 1)
        credential_attempted = False
        try:
            with self.entries.writing():
                if request["valid_until_ms"] <= self._now_ms():
                    raise SupervisorFailure(400, "the enrollment expiry must be in the future")
                plan = self._plan(request["plan_id"])
                owner_id = self._owner(actor, plan)
                context = self._eligible(plan, owner_id)
                self._expected_context(request, context)
                grant = self._grant(request, plan, context, owner_id, grant_id, 1)
                credential_attempted = True
                self.secrets_store.put(credential_name, token)
                self._record_grant(grant, token, credential_name, context, actor)
        except BaseException:
            if credential_attempted:
                self.secrets_store.drop([credential_name])
            raise
        return grant, token

    def change(self, actor: Actor, body: object) -> tuple[dict[str, Any], str | None]:
        request = self._change(body)
        rotated_name = ""
        old_name = ""
        token: str | None = None
        try:
            with self.entries.writing():
                entry = self._latest_entry(request["grant_id"])
                if entry is None:
                    raise SupervisorFailure(403, "supervisor request is not authorized")
                current = self._public_grant(entry)
                plan = self._plan(current["plan_id"])
                owner_id = self._owner(actor, plan)
                if current["grant_version"] != request["expected_grant_version"]:
                    raise SupervisorFailure(409, "the supervisor grant changed; read it again before changing it")
                if current["revoked"] or current["mode"] == "disabled":
                    raise SupervisorFailure(409, "the supervisor grant is already revoked")

                next_version = current["grant_version"] + 1
                old_name = entry.data.get("_credential_name", "")
                if request["change"]["kind"] == "revoke":
                    grant = {**current, "grant_version": next_version, "mode": "disabled", "revoked": True}
                    self._append_grant(grant, "", "", entry.data, actor)
                else:
                    replacement = self._enrollment(request["change"]["enrollment"])
                    if replacement["valid_until_ms"] <= self._now_ms():
                        raise SupervisorFailure(400, "the enrollment expiry must be in the future")
                    replacement_plan = self._plan(replacement["plan_id"])
                    replacement_owner = self._owner(actor, replacement_plan)
                    if replacement_owner != owner_id:
                        raise SupervisorFailure(403, "supervisor request is not authorized")
                    context = self._eligible(replacement_plan, replacement_owner)
                    self._expected_context(replacement, context)
                    grant = self._grant(replacement, replacement_plan, context, owner_id, current["grant_id"], next_version)
                    token = secrets.token_urlsafe(32)
                    rotated_name = self._credential_name(grant["grant_id"], next_version)
                    self.secrets_store.put(rotated_name, token)
                    self._record_grant(grant, token, rotated_name, context, actor)
        except BaseException:
            if rotated_name:
                self.secrets_store.drop([rotated_name])
            raise
        if old_name:
            self.secrets_store.drop([old_name])
        return grant, token

    def authenticate(self, token: str) -> SupervisorPrincipal:
        if not token or len(token) > 512:
            raise SupervisorFailure(401, "a supervisor service credential is required")
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        for entry in self._latest_entries():
            if not hmac.compare_digest(str(entry.data.get("_credential_sha256", "")), digest):
                continue
            grant = self._public_grant(entry)
            principal = self._principal(grant)
            self.revalidate(principal)
            return principal
        raise SupervisorFailure(403, "the supervisor service credential is invalid or revoked")

    def revalidate(self, principal: SupervisorPrincipal, plan_id: int | None = None) -> dict[str, Any]:
        entry = self._latest_entry(principal.grant_id)
        if entry is None:
            raise SupervisorFailure(403, "the supervisor grant is no longer current")
        grant = self._public_grant(entry)
        if (grant["grant_version"] != principal.grant_version or grant["owner_user_id"] != principal.owner_user_id
                or grant["scope"] != principal.scope or grant["revoked"] or grant["mode"] == "disabled"
                or grant["valid_until_ms"] <= self._now_ms() or not entry.data.get("_credential_sha256")):
            raise SupervisorFailure(403, "the supervisor grant is no longer current")
        if plan_id is not None and plan_id != grant["plan_id"]:
            raise SupervisorFailure(403, "the supervisor grant does not cover that reference")
        plan = self._plan(grant["plan_id"])
        if self.owners.number(plan) != grant["owner_user_id"]:
            raise SupervisorFailure(403, "the supervisor grant no longer matches its owner or plan")
        context = self._eligible(plan, grant["owner_user_id"])
        if (grant["scope"] != self._scope(grant["owner_user_id"], context["driver_environment_id"])
                or grant["driver_agent_id"] != context["agent"].row_id
                or grant["driver_environment_id"] != context["driver_environment_id"]
                or grant["driver_provider"] != context["agent"].provider
                or grant["current_phase"] != context["current_phase"]
                or entry.data.get("_expected_binding_revision") != context["binding_revision"]):
            raise SupervisorFailure(403, "the supervisor grant no longer matches the current plan state")
        for enrolled in grant["checks"]:
            try:
                check = self._check(enrolled["check_id"])
            except SupervisorFailure:
                raise SupervisorFailure(403, "the supervisor grant no longer matches its enrolled checks") from None
            if (self._check_revision(check) != enrolled["expected_revision"]
                    or self._command_hash(check.command) != enrolled["command_sha256"]
                    or not self._whole_minutes(check.interval)
                    or not enrolled["minimum_interval_minutes"] <= int(check.interval) <= enrolled["baseline_interval_minutes"]
                    or check.is_retired or check.wait_target):
                raise SupervisorFailure(403, "the supervisor grant no longer matches its enrolled checks")
        if self._template_revision(grant["diagnostic_template_id"]) != grant["diagnostic_template_revision"]:
            raise SupervisorFailure(403, "the supervisor grant no longer matches its diagnostic template")
        return grant

    def permits_domain_write(self, grant: dict[str, Any], operation: str) -> bool:
        if (operation.casefold() in RESERVED_OPERATIONS or grant.get("mode") != "bounded_write"
                or grant.get("revoked") or grant.get("valid_until_ms", 0) <= self._now_ms()):
            return False
        capability = SUPPORTED_OPERATIONS.get(operation)
        return bool(capability and grant.get("capabilities", {}).get(capability) is True)

    def permits_proposal_receipt(self, grant: dict[str, Any]) -> bool:
        return grant.get("mode") == "shadow" and not grant.get("revoked") and grant.get("valid_until_ms", 0) > self._now_ms()

    def _expected_context(self, request: dict[str, Any], context: dict[str, Any]) -> None:
        if (request["current_phase"] != context["current_phase"]
                or request["expected_plan_revision"] != context["plan_revision"]
                or request["expected_binding_revision"] != context["binding_revision"]):
            raise SupervisorFailure(409, "the plan changed; refresh its current phase and revisions")
        for enrolled in request["checks"]:
            try:
                check = self._check(enrolled["check_id"])
            except SupervisorFailure:
                raise SupervisorFailure(409, "an enrolled check changed; refresh its revision") from None
            if (self._check_revision(check) != enrolled["expected_revision"]
                    or self._command_hash(check.command) != enrolled["command_sha256"]
                    or not self._whole_minutes(check.interval)
                    or int(check.interval) != enrolled["baseline_interval_minutes"]
                    or check.is_retired or check.wait_target
                    or enrolled["minimum_interval_minutes"] > enrolled["baseline_interval_minutes"]):
                raise SupervisorFailure(409, "an enrolled check does not match its current command and range")
        if request["diagnostic_template_revision"] != self._template_revision(request["diagnostic_template_id"]):
            raise SupervisorFailure(409, "the diagnostic template changed; refresh its revision")

    def _eligible(self, plan: Plan, owner_id: int) -> dict[str, Any]:
        if not owner_id or plan.state != PlanState.STARTED or plan.mode != PlanMode.SOLO or self.bindings.is_ended(plan):
            raise SupervisorFailure(409, "the plan is not eligible for supervisor enrollment")
        driver_environment_id = self.bindings.environment_id(plan)
        if not driver_environment_id:
            raise SupervisorFailure(409, "the plan is not eligible for supervisor enrollment")
        with self.scope.environment(plan.environment_id):
            current_plan = self.plans.find(plan.row_id)
            phases = self.plans.phase_states(current_plan)
            phase_number = current_plan.current_phase(phases)
            phase_state = next((phase for phase in phases if phase.number == phase_number), None)
            if (phase_state is None or not phase_state.has_open_work() or self.plans.checkpoint_plans(current_plan)
                    or self.phase_testing.unpassed(current_plan)):
                raise SupervisorFailure(409, "the plan is not eligible for supervisor enrollment")
            plan_revision = self._plan_revision(current_plan, phases)
            phase_revision = self._phase_revision(current_plan, phase_state)
            current_phase = {"phase_id": phase_state.phase.row_id, "number": phase_state.number, "revision": phase_revision}
        with self.scope.environment(driver_environment_id):
            agent = self.agents.agent(current_plan)
            environment = self.agents.environment(current_plan)
            if (agent is None or environment is None or environment.row_id != driver_environment_id
                    or agent.environment_id != driver_environment_id or agent.role.value != "main"
                    or agent.creator != Actor.user(owner_id) or agent.provider != "codex" or not agent.session or agent.state != "leading_plan"
                    or not self.agents.is_running(environment)):
                raise SupervisorFailure(409, "the plan is not eligible for supervisor enrollment")
        binding_revision = self._binding_revision(current_plan, agent, environment)
        return {
            "plan": current_plan,
            "agent": agent,
            "environment": environment,
            "driver_environment_id": driver_environment_id,
            "current_phase": current_phase,
            "plan_revision": plan_revision,
            "binding_revision": binding_revision,
            "owner_user_id": owner_id,
        }

    def _plan_revision(self, plan: Plan, phases) -> str:
        with self.scope.environment(plan.environment_id):
            phase_rows = []
            for state in phases:
                phase = state.phase
                tasks = self.plans.phase_tasks(phase)
                links = self.links.ref_links("target", [Ref.build(phase)], PHASE_LINK)
                phase_rows.append({
                    "number": state.number,
                    "phase": self._phase_values(phase),
                    "links": [self._link_values(link) for link in links],
                    "tasks": [self._task_values(task) for task in tasks],
                })
            plan_links = self.links.source_links(plan, PLAN_LINK)
            phase_membership = self.links.typed_source_links(plan, PHASE_TASK_LINK, Phase.table())
            plan_tasks = self.plans.plan_tasks(plan)
            return self._digest({
                "plan": self._plan_values(plan),
                "phase_membership": [self._link_values(link) for link in phase_membership],
                "phases": phase_rows,
                "plan_task_links": [self._link_values(link) for link in plan_links],
                "plan_tasks": [self._task_values(task) for task in plan_tasks],
            })

    def _phase_revision(self, plan: Plan, phase_state) -> str:
        phase_links = self.links.ref_links("target", [Ref.build(phase_state.phase)], PHASE_LINK)
        membership = self.links.typed_source_links(plan, PHASE_TASK_LINK, Phase.table())
        return self._digest({
            "phase_id": phase_state.phase.row_id,
            "number": phase_state.number,
            "phase": self._phase_values(phase_state.phase),
            "phase_order": [self._link_values(link) for link in membership],
            "phase_tasks": [self._link_values(link) for link in phase_links],
        })

    def _binding_revision(self, plan: Plan, agent: Agent, environment) -> str:
        bindings = [*self.links.source_links(plan, BOUND_LINK), *self.links.source_links(plan, ENDED_LINK), *self.links.source_links(plan, PLAN_AGENT_LINK)]
        return self._digest({
            "links": [self._link_values(link) for link in bindings],
            "agent": self._agent_values(agent),
            "environment": {"id": environment.row_id, "key": environment.key, "type": environment.environment_type.value},
        })

    def _check_revision(self, check: Check) -> str:
        return self._digest({
            "id": check.row_id, "title": check.title, "brief": check.brief, "command": check.command,
            "wait_target": check.wait_target, "retired": check.is_retired,
        })

    def _template_revision(self, template_id: str) -> str:
        template = self._template(template_id)
        if template is None:
            raise SupervisorFailure(409, "the diagnostic template is unavailable")
        return self._digest({
            "id": template.row_id, "title": template.title, "targets": template.targets, "purpose": template.purpose,
            "brief": template.brief, "parts": template.parts, "commands": template.commands,
            "schedule": template.schedule.value, "updated_at": self._date(template.updated_at),
        })

    def _template(self, template_id: str) -> Template | None:
        if template_id.isdigit():
            rows = self.templates.selected(self.templates.query().filter(id=int(template_id)).limit(1))
            return rows[0] if rows else None
        rows = self.templates.matching(title=template_id)
        return rows[0] if len(rows) == 1 else None

    def _grant(self, request: dict[str, Any], plan: Plan, context: dict[str, Any], owner_id: int, grant_id: str, version: int) -> dict[str, Any]:
        scope = self._scope(owner_id, context["driver_environment_id"])
        return {
            "protocol_version": 1,
            "grant_id": grant_id,
            "grant_version": version,
            "owner_user_id": owner_id,
            "scope": scope,
            "plan_id": plan.row_id,
            "driver_agent_id": context["agent"].row_id,
            "driver_environment_id": context["driver_environment_id"],
            "driver_provider": "codex",
            "current_phase": request["current_phase"],
            "checks": request["checks"],
            "diagnostic_template_id": request["diagnostic_template_id"],
            "diagnostic_template_revision": request["diagnostic_template_revision"],
            "capabilities": request["capabilities"],
            "limits": request["limits"],
            "mode": request["mode"],
            "valid_until_ms": request["valid_until_ms"],
            "revoked": False,
        }

    def _record_grant(self, grant: dict[str, Any], token: str, credential_name: str, context: dict[str, Any], actor: Actor) -> None:
        data = {
            **grant,
            "_credential_sha256": hashlib.sha256(token.encode("utf-8")).hexdigest(),
            "_credential_name": credential_name,
            "_expected_plan_revision": context["plan_revision"],
            "_expected_binding_revision": context["binding_revision"],
        }
        self._append_grant(grant, data["_credential_sha256"], credential_name, data, actor)

    def _append_grant(self, grant: dict[str, Any], digest: str, credential_name: str, prior_data: dict[str, Any], actor: Actor) -> None:
        data = {
            **grant,
            "_credential_sha256": digest,
            "_credential_name": credential_name,
            "_expected_plan_revision": prior_data.get("_expected_plan_revision", ""),
            "_expected_binding_revision": prior_data.get("_expected_binding_revision", ""),
        }
        environment_id = grant["driver_environment_id"]
        with self.scope.environment(environment_id):
            self.control_entries.recorded(Entry(environment_id=environment_id, entry_type=GRANT_ENTRY, actor=actor,
                data=data, idempotency=f"supervisor:grant:{grant['grant_id']}:{grant['grant_version']}"), actor)

    def _public_grant(self, entry: Entry) -> dict[str, Any]:
        return {key: entry.data[key] for key in GRANT_FIELDS if key in entry.data}

    def _latest_entry(self, grant_id: str) -> Entry | None:
        rows = [entry for entry in self._latest_entries() if entry.data.get("grant_id") == grant_id]
        return max(rows, key=lambda row: (row.data.get("grant_version", 0), row.row_id)) if rows else None

    def _latest_entries(self) -> list[Entry]:
        rows = self.entries.selected_globally(self.entries.query().filter(entry_type=GRANT_ENTRY).order("id"))
        latest: dict[str, Entry] = {}
        for entry in rows:
            grant_id = entry.data.get("grant_id")
            if not isinstance(grant_id, str) or not grant_id:
                continue
            previous = latest.get(grant_id)
            if previous is None or (entry.data.get("grant_version", 0), entry.row_id) > (previous.data.get("grant_version", 0), previous.row_id):
                latest[grant_id] = entry
        return list(latest.values())

    def _principal(self, grant: dict[str, Any]) -> SupervisorPrincipal:
        return SupervisorPrincipal(grant["grant_id"], grant["grant_version"], grant["owner_user_id"], grant["scope"], Actor.plugin(SUPERVISOR_ACTOR))

    def _scope(self, owner_id: int, environment_id: int) -> dict[str, Any]:
        project_id = self.secrets_store.project_id()
        return {
            "tenant_id": f"owner:{owner_id}",
            "project_id": project_id,
            "environment_id": environment_id,
            "manager_id": MANAGER_ID,
            "writer_node_id": project_id,
            "installation_epoch": INSTALLATION_EPOCH,
        }

    def _owner(self, actor: Actor, plan: Plan) -> int:
        owner_id = self.owners.number(plan)
        if actor.actor_type != ActorType.USER or not owner_id or not actor.id.isdigit() or int(actor.id) != owner_id:
            raise SupervisorFailure(403, "supervisor request is not authorized")
        return owner_id

    def _plan(self, plan_id: int) -> Plan:
        rows = self.plans.selected_globally(self.plans.query().filter(id=plan_id).limit(1))
        if not rows:
            raise SupervisorFailure(403, "supervisor request is not authorized")
        return rows[0]

    def _check(self, check_id: int) -> Check:
        rows = self.checks.selected(self.checks.query().filter(id=check_id).limit(1))
        if not rows:
            raise SupervisorFailure(409, "an enrolled check is unavailable")
        return rows[0]

    def _plan_values(self, plan: Plan) -> dict[str, Any]:
        return {
            "id": plan.row_id, "title": plan.title, "brief": plan.brief, "state": plan.state.value,
            "mode": plan.mode.value, "block_reason": plan.block_reason, "driver": plan.driver,
            "driver_agent": plan.driver_agent, "priorities": plan.priorities, "priorities_phase": plan.priorities_phase,
            "updated_at": self._date(plan.updated_at), "updater": plan.updater.stamp if plan.updater else "",
        }

    def _phase_values(self, phase: Phase) -> dict[str, Any]:
        return {
            "id": phase.row_id, "title": phase.title, "completion_rule": phase.completion_rule,
            "checkpoint": phase.checkpoint, "updated_at": self._date(phase.updated_at),
            "updater": phase.updater.stamp if phase.updater else "",
        }

    def _task_values(self, task) -> dict[str, Any]:
        return {
            "id": task.row_id, "title": task.title, "brief": task.brief, "state": task.state.value,
            "delegated": task.delegated, "updated_at": self._date(task.updated_at),
            "updater": task.updater.stamp if task.updater else "",
        }

    def _agent_values(self, agent: Agent) -> dict[str, Any]:
        return {
            "id": agent.row_id, "environment_id": agent.environment_id, "role": agent.role.value,
            "provider": agent.provider, "session": agent.session,
        }

    def _link_values(self, link: Link) -> dict[str, Any]:
        return {
            "id": link.row_id, "source": self._ref_value(link.source), "target": self._ref_value(link.target),
            "kind": link.link_type, "created_at": self._date(link.created_at), "updated_at": self._date(link.updated_at),
        }

    @staticmethod
    def _ref_value(ref: Ref) -> dict[str, Any]:
        return {"table": ref.type, "id": ref.id}

    @staticmethod
    def _date(value: datetime | None) -> str:
        return value.isoformat() if value else ""

    @staticmethod
    def _digest(value: Any) -> str:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _command_hash(command: str) -> str:
        return hashlib.sha256(command.encode("utf-8")).hexdigest()

    @staticmethod
    def _whole_minutes(value: float) -> bool:
        return value > 0 and float(value).is_integer()

    def _credential_name(self, grant_id: str, version: int) -> str:
        return f"JOURNAL_SUPERVISOR_{grant_id.upper()}_{version}"

    def _now_ms(self) -> int:
        return int(self.time_source.seconds() * 1000)

    @classmethod
    def _enrollment(cls, value: object) -> dict[str, Any]:
        keys = {"protocol_version", "plan_id", "current_phase", "expected_plan_revision", "expected_binding_revision", "checks", "diagnostic_template_id", "diagnostic_template_revision", "capabilities", "limits", "mode", "valid_until_ms"}
        body = cls._object(value, keys)
        if not isinstance(body["protocol_version"], int) or isinstance(body["protocol_version"], bool) or body["protocol_version"] != 1:
            raise SupervisorFailure(400, "the enrollment request does not match supervisor protocol version 1")
        cls._integer(body["plan_id"], 1)
        cls._string(body["expected_plan_revision"], 256)
        cls._string(body["expected_binding_revision"], 256)
        phase = cls._object(body["current_phase"], {"phase_id", "number", "revision"})
        cls._integer(phase["phase_id"], 1)
        cls._integer(phase["number"], 1)
        cls._string(phase["revision"], 256)
        checks = body["checks"]
        if not isinstance(checks, list) or not 1 <= len(checks) <= 4:
            raise SupervisorFailure(400, "the enrollment request does not match supervisor protocol version 1")
        parsed_checks, seen = [], set()
        for raw in checks:
            check = cls._object(raw, CHECK_FIELDS)
            cls._integer(check["check_id"], 1)
            if check["check_id"] in seen:
                raise SupervisorFailure(400, "the enrollment request does not match supervisor protocol version 1")
            seen.add(check["check_id"])
            if not isinstance(check["command_sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", check["command_sha256"]):
                raise SupervisorFailure(400, "the enrollment request does not match supervisor protocol version 1")
            cls._integer(check["baseline_interval_minutes"], 5, 30)
            cls._integer(check["minimum_interval_minutes"], 5, 30)
            cls._string(check["expected_revision"], 256)
            parsed_checks.append(dict(check))
        template_id = cls._string(body["diagnostic_template_id"], 256)
        template_revision = cls._string(body["diagnostic_template_revision"], 256)
        capabilities = cls._object(body["capabilities"], CAPABILITY_FIELDS)
        if capabilities != {"diagnostic_task": True, "plan_priorities": True, "check_interval": True, "sequence": False, "phrase_nudge": False, "project_reminder": False}:
            raise SupervisorFailure(400, "the enrollment request asks for an unsupported supervisor capability")
        limits = cls._object(body["limits"], BUDGET_FIELDS)
        for key, amount in limits.items():
            cls._integer(amount, 1)
        if limits["max_new_diagnostics_per_episode"] != 1:
            raise SupervisorFailure(400, "the enrollment request does not match supervisor protocol version 1")
        if body["mode"] not in ("shadow", "bounded_write"):
            raise SupervisorFailure(400, "the enrollment request does not match supervisor protocol version 1")
        cls._integer(body["valid_until_ms"], 1)
        return {**body, "current_phase": dict(phase), "checks": parsed_checks, "diagnostic_template_id": template_id,
                "diagnostic_template_revision": template_revision, "capabilities": dict(capabilities), "limits": dict(limits)}

    @classmethod
    def _change(cls, value: object) -> dict[str, Any]:
        body = cls._object(value, {"protocol_version", "grant_id", "expected_grant_version", "change"})
        if not isinstance(body["protocol_version"], int) or isinstance(body["protocol_version"], bool) or body["protocol_version"] != 1:
            raise SupervisorFailure(400, "the grant change does not match supervisor protocol version 1")
        grant_id = cls._string(body["grant_id"], 256)
        cls._integer(body["expected_grant_version"], 1)
        change = body["change"]
        if not isinstance(change, dict) or change.get("kind") not in ("revoke", "replace"):
            raise SupervisorFailure(400, "the grant change does not match supervisor protocol version 1")
        if change["kind"] == "revoke":
            change = cls._object(change, {"kind"})
        else:
            change = cls._object(change, {"kind", "enrollment"})
        return {**body, "grant_id": grant_id, "change": dict(change)}

    @staticmethod
    def _object(value: object, keys: frozenset[str] | set[str]) -> dict[str, Any]:
        if not isinstance(value, dict) or set(value) != set(keys):
            raise SupervisorFailure(400, "the request does not match supervisor protocol version 1")
        return value

    @staticmethod
    def _integer(value: object, minimum: int, maximum: int | None = None) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or value < minimum or maximum is not None and value > maximum:
            raise SupervisorFailure(400, "the request does not match supervisor protocol version 1")
        return value

    @staticmethod
    def _string(value: object, maximum: int) -> str:
        if not isinstance(value, str) or not value or len(value) > maximum:
            raise SupervisorFailure(400, "the request does not match supervisor protocol version 1")
        return value
