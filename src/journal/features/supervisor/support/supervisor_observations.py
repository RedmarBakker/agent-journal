import hashlib
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from journal.features.supervisor.support.admissions import MAX_OBSERVATION_AGE
from journal.features.supervisor.support.supervisor_action_reports import SupervisorActionReports
from journal.features.supervisor.support.supervisor_episode_qualification import OBSERVATION_ENTRY, SupervisorEpisodeQualification
from journal.models.check import Check
from journal.models.entry import Entry
from journal.events.rows.check_completed import CheckCompleted
from journal.events.rows.check_run_changed import CheckRunChanged
from journal.repositories.entries import Entries
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.support.actor import Actor
from journal.support.masks import Masks
from journal.support.time_source import TimeSource
from journal.supervisor_authority import SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from journal.supervisor_principal import SupervisorPrincipal

PAGE_SIZE = 100
OUTPUT_CHARACTERS = 16_384
EVIDENCE_RETENTION_MS = 30 * 24 * 60 * 60 * 1000
MAX_ACTION_AGE_MS = MAX_OBSERVATION_AGE * 1000
EVIDENCE_ACTOR = Actor.plugin("journal-supervisor")


class SupervisorObservations:
    """Captures check evidence with its result and reads bounded, grant-scoped observation pages."""

    def __init__(self, authority: SupervisorAuthority, entries: Entries, control_entries: SupervisorEntries,
                 scope: Scope, masks: Masks, time_source: TimeSource,
                 episode_qualification: SupervisorEpisodeQualification,
                 action_reports: SupervisorActionReports) -> None:
        self.authority, self.entries, self.control_entries = authority, entries, control_entries
        self.scope, self.masks, self.time_source = scope, masks, time_source
        self.episode_qualifier = episode_qualification
        self.action_reports = action_reports

    def completed(self, check: Check, event: CheckCompleted, started: float, fault: str) -> None:
        self._capture(check, event.check_id, started, event.time, event.passed, event.output, fault, False)

    def stopped(self, check: Check, event: CheckRunChanged) -> None:
        self._capture(check, event.check_id, event.run_start, event.time, False, check.last_output, "", True)

    def observe(self, principal: SupervisorPrincipal, body: object) -> dict[str, Any]:
        request = self._request(body)
        grant = self.authority.revalidate(principal)
        run, installation_epoch = self._run(principal, grant, request)
        snapshot = self.authority.observation_snapshot(principal, installation_epoch)
        qualification = self.episode_qualifier.qualify(grant, installation_epoch)
        snapshot = {**snapshot, "episode_qualification": qualification,
            "progress_watermark_ms": qualification["progress_watermark_ms"]}
        page = self._page(grant, installation_epoch, request["cursor"])
        return {
            "protocol_version": 1,
            "run": self._run_result(run, installation_epoch),
            "snapshot": snapshot,
            "page": page,
            "server_now_ms": self._now_ms(),
        }

    def action_run(self, principal: SupervisorPrincipal, grant: dict[str, Any], request: dict[str, Any]) -> tuple[Entry, int]:
        run, epoch = self._run(principal, grant, {
            "run_id": request["run_id"], "installation_epoch": request["installation_epoch"], "fence": request["fence"],
        })
        with self.scope.environment(PROJECT):
            states = self.entries.supervisor_records(
                "SupervisorRunState", last=1, tenant_id=principal.scope["tenant_id"], run_ref=request["run_id"],
            )
        if states and states[0].data.get("status") in ("complete", "conflicted", "rejected"):
            raise SupervisorFailure(403, "supervisor run is not current")
        return run, epoch

    def action_evidence(self, principal: SupervisorPrincipal, grant: dict[str, Any], installation_epoch: int,
                        observation_ids: list[str]) -> list[Entry]:
        if len(observation_ids) != len(set(observation_ids)):
            raise SupervisorFailure(400, "the supervisor action evidence is invalid")
        now_ms = self._now_ms()
        found = []
        with self.scope.environment(PROJECT):
            for observation_id in sorted(observation_ids):
                rows = self.entries.supervisor_records(
                    OBSERVATION_ENTRY, last=1, tenant_id=principal.scope["tenant_id"],
                    project_id=principal.scope["project_id"], environment_id=principal.scope["environment_id"],
                    manager_id=principal.scope["manager_id"], node_id=principal.scope["writer_node_id"],
                    installation_epoch=installation_epoch, grant_id=grant["grant_id"],
                    grant_version=grant["grant_version"], plan_id=grant["plan_id"], observation_id=observation_id,
                )
                if not rows or not self._qualifying_action_evidence(rows[0], grant, installation_epoch, now_ms):
                    raise SupervisorFailure(403, "supervisor action evidence is not current")
                found.append(rows[0])
        return found

    def record_episode_attempt(self, principal: SupervisorPrincipal, episode_id: str, attempt_id: str) -> dict[str, Any]:
        return self.episode_qualification.record_attempt(principal, episode_id, attempt_id)

    def episode_qualification(self, principal: SupervisorPrincipal, installation_epoch: int) -> dict[str, Any]:
        grant = self.authority.revalidate(principal)
        return self.episode_qualifier.qualify(grant, installation_epoch)

    @staticmethod
    def _qualifying_action_evidence(entry: Entry, grant: dict[str, Any], installation_epoch: int, now_ms: int) -> bool:
        data = entry.data
        observation = data.get("observation", {})
        facts = observation.get("facts", {}) if isinstance(observation, dict) else {}
        if not isinstance(facts, dict):
            return False
        captured = data.get("committed_at_ms")
        enrolled = next((item for item in grant["checks"] if item["check_id"] == data.get("check_id")), None)
        return bool(
            enrolled and data.get("plan_id") == grant["plan_id"]
            and data.get("grant_id") == grant["grant_id"] and data.get("grant_version") == grant["grant_version"]
            and data.get("stopped") is False and facts.get("verdict") in ("failed", "faulted")
            and data.get("command_sha256") == enrolled["command_sha256"] and facts.get("check_id") == data.get("check_id")
            and type(captured) is int and 0 <= now_ms - captured <= MAX_ACTION_AGE_MS
            and type(data.get("expires_at_ms")) is int and data["expires_at_ms"] > now_ms
            and type(data.get("evidence_generation")) is int and data["evidence_generation"] > 0
            and observation.get("observation_id") == data.get("observation_id")
            and observation.get("plan_id") == grant["plan_id"]
            and observation.get("scope") == {**grant["scope"], "installation_epoch": installation_epoch}
        )

    def _capture(self, check: Check, check_id: int, started: float, completed: float, passed: bool,
                 output: str, fault: str, stopped: bool) -> None:
        if check.row_id != check_id:
            return
        for candidate in self.authority.observation_candidates(check):
            grant = candidate["grant"]
            context = self.authority.observation_context(grant)
            with self.scope.environment(PROJECT):
                installation = self.entries.supervisor_records("SupervisorInstallation", last=1, tenant_id=grant["scope"]["tenant_id"])
                install = installation[0].data if installation else {}
                epoch = install.get("epoch", grant["scope"]["installation_epoch"])
                if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
                    continue
                if (install.get("installation_epoch_rotated") is True
                        and (install.get("management_writes_enabled") is not True
                             or install.get("restore_review_required") is True)):
                    continue
                self._record(check, candidate, context, epoch, started, completed, passed, output, fault, stopped, install)

    def _record(self, check: Check, candidate: dict[str, Any], context: dict[str, Any], epoch: int,
                started: float, completed: float, passed: bool, output: str, fault: str,
                stopped: bool, installation: dict[str, Any]) -> None:
        grant = candidate["grant"]
        captured_at = int(completed * 1000)
        observation_id = uuid.uuid4().hex
        output_excerpt = self._redacted(output)[-OUTPUT_CHARACTERS:]
        output_sha256 = hashlib.sha256(output_excerpt.encode("utf-8")).hexdigest()
        check_revision = self.authority._check_revision(check)
        command_sha256 = self.authority._command_hash(check.command)
        context_revision = self._digest({
            "check_revision": check_revision,
            "command_sha256": command_sha256,
            "context": context,
        })
        generation = self._next_generation(grant, check.row_id, epoch)
        scope = {**grant["scope"], "installation_epoch": epoch}
        facts = {
            "check_id": check.row_id,
            "run_id": observation_id,
            "started_at_ms": int(started * 1000),
            "completed_at_ms": captured_at,
            "verdict": "stopped" if stopped else "passed" if passed else "faulted" if fault else "failed",
            "exit_status": None,
            "command_sha256": command_sha256,
            "output_excerpt": output_excerpt,
            "output_sha256": output_sha256,
        }
        observation = {
            "protocol_version": 1,
            "observation_id": observation_id,
            "scope": scope,
            "plan_id": grant["plan_id"],
            "source_ref": {"table": "checks", "id": check.row_id},
            "source_revision": context_revision,
            "committed_at_ms": captured_at,
            "captured_at_ms": captured_at,
            "evidence_generation": generation,
            "kind": "check_completed",
            "facts": facts,
        }
        data = {
            "tenant_id": scope["tenant_id"],
            "project_id": scope["project_id"],
            "environment_id": scope["environment_id"],
            "manager_id": scope["manager_id"],
            "node_id": scope["writer_node_id"],
            "installation_id": installation.get("installation_id", ""),
            "installation_epoch": epoch,
            "grant_id": grant["grant_id"],
            "grant_version": grant["grant_version"],
            "plan_id": grant["plan_id"],
            "check_id": check.row_id,
            "run_id": observation_id,
            "observation_id": observation_id,
            "evidence_generation": generation,
            "committed_at_ms": captured_at,
            "expires_at_ms": captured_at + EVIDENCE_RETENTION_MS,
            "retention_policy": "supervisor-check-evidence-30-days",
            "fault": self._redacted(fault)[-OUTPUT_CHARACTERS:],
            "stopped": stopped,
            "check_revision": check_revision,
            "command_sha256": command_sha256,
            "object_revisions": {
                "check": check_revision,
                "plan": context["plan_revision"],
                "phase": context["phase"]["revision"] if context["phase"] else "",
                "binding": context["binding_revision"],
                "tasks": context["tasks"],
                "review": context["review"]["revision"],
            },
            "context": context,
            "observation": observation,
        }
        key = f"supervisor:observation:{grant['grant_id']}:{epoch}:{observation_id}"
        stored = self.control_entries.recorded(Entry(environment_id=PROJECT, entry_type=OBSERVATION_ENTRY,
            actor=EVIDENCE_ACTOR, data=data, idempotency=key), EVIDENCE_ACTOR)
        self.episode_qualifier.qualify(grant, epoch)
        self.action_reports.measure(grant, stored)

    def _next_generation(self, grant: dict[str, Any], check_id: int, epoch: int) -> int:
        rows = self.entries.supervisor_records(
            OBSERVATION_ENTRY, last=1, grant_id=grant["grant_id"], grant_version=grant["grant_version"], check_id=check_id, installation_epoch=epoch,
        )
        return int(rows[0].data.get("evidence_generation", 0)) + 1 if rows else 1

    def _run(self, principal: SupervisorPrincipal, grant: dict[str, Any], request: dict[str, Any]) -> tuple[Entry, int]:
        scope = principal.scope
        with self.scope.environment(PROJECT):
            runs = self.entries.supervisor_records(
                "SupervisorRun", last=100, tenant_id=scope["tenant_id"], run_ref=request["run_id"],
            )
            installation_rows = self.entries.supervisor_records("SupervisorInstallation", last=1, tenant_id=scope["tenant_id"])
            if not runs or not installation_rows:
                raise SupervisorFailure(403, "supervisor run is not current")
            run = runs[0]
            data = run.data
            installation = installation_rows[0].data
            if (installation.get("installation_epoch_rotated") is True
                    and (installation.get("management_writes_enabled") is not True
                         or installation.get("restore_review_required") is True)):
                raise SupervisorFailure(403, "supervisor management writes await owner review")
            epoch = data.get("installation_epoch")
            current_epoch = installation.get("epoch")
            current_runs = self.entries.supervisor_records(
                "SupervisorRun", last=100, tenant_id=scope["tenant_id"], plan_id=grant["plan_id"], node_id=scope["writer_node_id"],
            )
        lease = self._date(data.get("lease_until"))
        now = datetime.fromtimestamp(self.time_source.seconds(), timezone.utc)
        if (data.get("grant_id") != grant["grant_id"] or data.get("grant_version") != grant["grant_version"]
                or data.get("plan_id") != grant["plan_id"] or data.get("node_id") != scope["writer_node_id"]
                or epoch != request["installation_epoch"] or current_epoch != request["installation_epoch"]
                or data.get("fence") != request["fence"] or not current_runs
                or current_runs[0].data.get("run_ref") != request["run_id"]
                or current_runs[0].data.get("fence") != request["fence"]
                or lease is None or lease <= now):
            raise SupervisorFailure(403, "supervisor run is not current")
        return run, current_epoch

    def _run_result(self, run: Entry, installation_epoch: int) -> dict[str, Any]:
        data = run.data
        reservation = data.get("reservation", {})
        try:
            reserved_cost = int(Decimal(str(reservation["cost_usd"])) * 1_000_000)
        except (KeyError, InvalidOperation, ValueError, TypeError):
            raise SupervisorFailure(403, "supervisor run reservation is not current") from None
        lease = self._date(data.get("lease_until"))
        if reserved_cost < 1 or lease is None:
            raise SupervisorFailure(403, "supervisor run reservation is not current")
        action_id = data.get("pending_action_id") or data.get("action_id") or f"observe:{self._digest(data['run_ref'])[:32]}"
        return {
            "run_id": data["run_ref"],
            "episode_id": data["episode_id"],
            "pending_action_id": action_id,
            "grant_id": data["grant_id"],
            "grant_version": data["grant_version"],
            "installation_epoch": installation_epoch,
            "fence": data["fence"],
            "lease_expires_at_ms": int(lease.timestamp() * 1000),
            "budget_reservation_id": str(data.get("budget_reservation_id") or f"reservation:{run.row_id}"),
            "reserved_cost_microusd": reserved_cost,
        }

    def _page(self, grant: dict[str, Any], epoch: int, cursor: str | None) -> dict[str, Any]:
        filters = {
            "tenant_id": grant["scope"]["tenant_id"],
            "project_id": grant["scope"]["project_id"],
            "environment_id": grant["scope"]["environment_id"],
            "manager_id": grant["scope"]["manager_id"],
            "grant_id": grant["grant_id"],
            "grant_version": grant["grant_version"],
            "plan_id": grant["plan_id"],
            "node_id": grant["scope"]["writer_node_id"],
            "installation_epoch": epoch,
        }
        now_ms = self._now_ms()
        with self.scope.environment(PROJECT):
            after_id = self._cursor_id(cursor, filters)
            rows = self.entries.supervisor_page(OBSERVATION_ENTRY, PAGE_SIZE, after_id=after_id, unexpired_after_ms=now_ms, **filters)
            query = self.entries.query().filter(entry_type=OBSERVATION_ENTRY)
            for key, value in filters.items():
                query = query.filter_json(f"data->{key}", value)
            query = query.filter_greater("data->expires_at_ms", now_ms)
            watermark = int(self.entries.maximum(query, "data->committed_at_ms", 0))
        next_cursor = rows[-1].data["observation_id"] if len(rows) == PAGE_SIZE else None
        return {
            "protocol_version": 1,
            "cursor": cursor,
            "next_cursor": next_cursor,
            "node_heartbeat_at_ms": now_ms,
            "observation_watermark_ms": watermark,
            "observations": [row.data["observation"] for row in rows],
        }

    def _cursor_id(self, cursor: str | None, filters: dict[str, Any]) -> int:
        if cursor is None:
            return 0
        rows = self.entries.supervisor_records(OBSERVATION_ENTRY, last=1, observation_id=cursor, **filters)
        if not rows:
            raise SupervisorFailure(403, "supervisor observation cursor is not current")
        return rows[0].row_id

    def _request(self, body: object) -> dict[str, Any]:
        expected = {"protocol_version", "run_id", "installation_epoch", "fence", "cursor"}
        if not isinstance(body, dict) or set(body) != expected:
            raise SupervisorFailure(400, "the supervisor observation request is invalid")
        if (type(body["protocol_version"]) is not int or body["protocol_version"] != 1
                or not isinstance(body["run_id"], str) or not body["run_id"] or len(body["run_id"]) > 256
                or type(body["installation_epoch"]) is not int or body["installation_epoch"] < 1
                or type(body["fence"]) is not int or body["fence"] < 1
                or body["cursor"] is not None and (not isinstance(body["cursor"], str) or len(body["cursor"]) > 256)):
            raise SupervisorFailure(400, "the supervisor observation request is invalid")
        return body

    def _now_ms(self) -> int:
        return int(self.time_source.seconds() * 1000)

    def _redacted(self, text: str) -> str:
        return self.masks.replaced(text, self.masks.current())

    @staticmethod
    def _digest(value: object) -> str:
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

    @staticmethod
    def _date(value: object) -> datetime | None:
        if not isinstance(value, str):
            return None
        try:
            date = datetime.fromisoformat(value)
        except ValueError:
            return None
        return date.astimezone(timezone.utc) if date.tzinfo else None
