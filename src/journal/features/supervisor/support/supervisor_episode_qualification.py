from typing import Any

from journal.features.supervisor.support.admissions import MAX_OBSERVATION_AGE, canonical, digest
from journal.repositories.entries import Entries
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from journal.supervisor_authority import SupervisorAuthority, SUPERVISOR_ACTOR
from journal.supervisor_principal import SupervisorPrincipal
from journal.models.entry import Entry


OBSERVATION_ENTRY = "SupervisorObservation"
MAX_EPISODE_ATTEMPTS = 2


class SupervisorEpisodeQualification:
    """Qualifies one actionable episode from durable check and task evidence."""

    def __init__(self, authority: SupervisorAuthority, entries: Entries, control_entries: SupervisorEntries,
                 scope: Scope, time_source: TimeSource) -> None:
        self.authority, self.entries, self.control_entries = authority, entries, control_entries
        self.scope, self.time_source = scope, time_source

    def qualify(self, grant: dict[str, Any], installation_epoch: int) -> dict[str, Any]:
        rows = self._observations(grant, installation_epoch)
        watermark = self._progress_watermark(rows)
        failures = self._failures_after(rows, watermark)
        if not failures:
            return {"status": "empty", "reason": "no_current_failure", "episode_id": "", "progress_watermark_ms": watermark}
        latest = failures[-1]
        context = latest.data.get("context", {})
        reason = self._stall_reason(context)
        fingerprint = self._fingerprint(grant, context, failures)
        episode_id = self._episode_id(grant, installation_epoch, context, fingerprint, watermark)
        generation = max(row.data["evidence_generation"] for row in failures)
        attempt_count = self._attempt_count(grant, episode_id)
        status = "needs_owner" if attempt_count >= MAX_EPISODE_ATTEMPTS else reason
        result = {
            "status": status,
            "reason": "attempt_limit_reached" if status == "needs_owner" else reason,
            "episode_id": episode_id,
            "problem_fingerprint": fingerprint,
            "progress_watermark_ms": watermark,
            "evidence_generation": generation,
            "observation_ids": [row.data["observation_id"] for row in failures[-20:]],
            "attempt_count": attempt_count,
        }
        self._record_qualification(grant, result, latest)
        return result

    def record_attempt(self, principal: SupervisorPrincipal, episode_id: str, attempt_id: str) -> dict[str, Any]:
        if not self._identifier(episode_id) or not self._identifier(attempt_id):
            return {"status": "skipped", "reason": "attempt_reference_invalid"}
        with self.scope.environment(PROJECT), self.entries.writing():
            grant = self.authority.revalidate(principal)
            current = self.qualify(grant, self._current_epoch(grant))
            if current["episode_id"] != episode_id:
                return {"status": "skipped", "reason": "episode_not_current"}
            if current["status"] != "actionable_stall":
                return {"status": "needs_owner" if current["status"] == "needs_owner" else "skipped", "reason": current["reason"], "attempt_count": current["attempt_count"]}
            key = self._attempt_key(grant, episode_id, attempt_id)
            if previous := self.entries.keyed(key):
                return self._attempt_result(previous[0], True)
            count = self._attempt_count(grant, episode_id)
            if count >= MAX_EPISODE_ATTEMPTS:
                return {"status": "needs_owner", "reason": "attempt_limit_reached", "attempt_count": count}
            count += 1
            row = self._record(grant, episode_id, "attempt", key, {
                "attempt_id": attempt_id,
                "attempt_count": count,
                "status": "admitted" if count < MAX_EPISODE_ATTEMPTS else "needs_owner",
                "reason": "" if count < MAX_EPISODE_ATTEMPTS else "attempt_limit_reached",
            })
            if count == MAX_EPISODE_ATTEMPTS:
                self._record(grant, episode_id, "escalation", self._escalation_key(grant, episode_id), {
                    "attempt_count": count,
                    "status": "needs_owner",
                    "reason": "attempt_limit_reached",
                })
            return self._attempt_result(row, False)

    def _observations(self, grant: dict[str, Any], installation_epoch: int) -> list[Entry]:
        with self.scope.environment(PROJECT):
            rows = self.entries.supervisor_records(
                OBSERVATION_ENTRY, last=100,
                tenant_id=grant["scope"]["tenant_id"], project_id=grant["scope"]["project_id"],
                environment_id=grant["scope"]["environment_id"], manager_id=grant["scope"]["manager_id"],
                node_id=grant["scope"]["writer_node_id"], installation_epoch=installation_epoch,
                grant_id=grant["grant_id"], grant_version=grant["grant_version"], plan_id=grant["plan_id"],
            )
        return sorted(rows, key=lambda row: (row.data.get("committed_at_ms", 0), row.row_id))

    def _progress_watermark(self, rows: list[Entry]) -> int:
        watermark = 0
        previous: dict[tuple[int, int], dict[str, Any]] = {}
        for row in rows:
            data = row.data
            observation = data.get("observation", {})
            facts = observation.get("facts", {}) if isinstance(observation, dict) else {}
            context = data.get("context", {})
            committed = data.get("committed_at_ms")
            if type(committed) is not int or not isinstance(context, dict):
                continue
            if data.get("stopped") is False and isinstance(facts, dict) and facts.get("verdict") == "passed":
                watermark = max(watermark, committed)
            phase = context.get("phase")
            phase_id = phase.get("id") if isinstance(phase, dict) else 0
            tasks = context.get("tasks", [])
            current: dict[tuple[int, int], dict[str, Any]] = {}
            if isinstance(tasks, list) and type(phase_id) is int:
                for task in tasks:
                    if not isinstance(task, dict) or task.get("phase_id") != phase_id or type(task.get("id")) is not int:
                        continue
                    key = (phase_id, task["id"])
                    current[key] = task
                    prior = previous.get(key)
                    state = task.get("state")
                    supervisor_write = task.get("updater") == Actor.plugin(SUPERVISOR_ACTOR).stamp
                    if (prior and prior.get("state") != state and state in ("started", "completed")
                            and not supervisor_write):
                        watermark = max(watermark, committed)
            previous = current
        return watermark

    def _failures_after(self, rows: list[Entry], watermark: int) -> list[Entry]:
        latest: dict[int, Entry] = {}
        now_ms = int(self.time_source.seconds() * 1000)
        for row in rows:
            data = row.data
            observation = data.get("observation", {})
            facts = observation.get("facts", {}) if isinstance(observation, dict) else {}
            committed = data.get("committed_at_ms")
            if (data.get("stopped") is not False or type(committed) is not int or committed <= watermark
                    or now_ms - committed < 0 or now_ms - committed > MAX_OBSERVATION_AGE * 1000 or not isinstance(facts, dict)
                    or facts.get("verdict") not in ("failed", "faulted") or type(data.get("check_id")) is not int):
                continue
            latest[data["check_id"]] = row
        return sorted(latest.values(), key=lambda row: (row.data["committed_at_ms"], row.row_id))

    def _stall_reason(self, context: dict[str, Any]) -> str:
        gates = context.get("gates", {})
        if not isinstance(gates, dict):
            return "owner_wait"
        if gates.get("explicit_owner_pause") is True:
            return "paused"
        if (context.get("plan_state") != "started" or gates.get("reserved_checkpoint") is True
                or gates.get("ended_drive") is True or gates.get("pending_owner_decision") is True
                or gates.get("unpassed_phase_commands")):
            return "owner_wait"
        phase = context.get("phase")
        phase_id = phase.get("id") if isinstance(phase, dict) else 0
        tasks = [task for task in context.get("tasks", []) if isinstance(task, dict) and task.get("phase_id") == phase_id]
        if any((isinstance(task.get("holder"), dict) and task["holder"].get("table") == "workers")
                or task.get("delegated") is True for task in tasks):
            return "busy_worker"
        if any(task.get("waits") for task in tasks):
            return "external_dependency"
        if any(task.get("state") == "paused" for task in tasks):
            return "paused"
        if context.get("started_task_id") is not None:
            return "busy_driver"
        if any(task.get("state") == "open" and task.get("holder") is None for task in tasks):
            return "actionable_stall"
        return "no_actionable_work"

    def _fingerprint(self, grant: dict[str, Any], context: dict[str, Any], failures: list[Entry]) -> str:
        phase = context.get("phase")
        intent = {
            "plan_id": grant["plan_id"],
            "phase_id": phase.get("id") if isinstance(phase, dict) else 0,
            "checks": sorted({
                (row.data["check_id"], row.data["command_sha256"])
                for row in failures
                if type(row.data.get("check_id")) is int and isinstance(row.data.get("command_sha256"), str)
            }),
        }
        return digest(canonical(intent) or "")

    def _episode_id(self, grant: dict[str, Any], epoch: int, context: dict[str, Any], fingerprint: str, watermark: int) -> str:
        phase = context.get("phase")
        intent = {
            "tenant_id": grant["scope"]["tenant_id"],
            "grant_id": grant["grant_id"],
            "grant_version": grant["grant_version"],
            "installation_epoch": epoch,
            "plan_id": grant["plan_id"],
            "phase_id": phase.get("id") if isinstance(phase, dict) else 0,
            "problem_fingerprint": fingerprint,
            "progress_watermark_ms": watermark,
        }
        return digest(canonical(intent) or "")[:32]

    def _record_qualification(self, grant: dict[str, Any], qualification: dict[str, Any], evidence: Entry) -> None:
        tenant_id = grant["scope"]["tenant_id"]
        episode_id = qualification["episode_id"]
        key = self._qualification_key(grant, episode_id, evidence.data["observation_id"])
        self._record(grant, episode_id, "qualification", key, {
            **qualification,
            "grant_id": grant["grant_id"],
            "grant_version": grant["grant_version"],
            "plan_id": grant["plan_id"],
            "tenant_id": tenant_id,
            "installation_epoch": evidence.data["installation_epoch"],
            "observation_id": evidence.data["observation_id"],
            "recorded_at_ms": int(self.time_source.seconds() * 1000),
        })

    def _record(self, grant: dict[str, Any], episode_id: str, kind: str, key: str, data: dict[str, Any]) -> Entry:
        actor = Actor.plugin(SUPERVISOR_ACTOR)
        with self.scope.environment(PROJECT):
            return self.control_entries.recorded(Entry(
                environment_id=PROJECT,
                entry_type="SupervisorEpisode",
                actor=actor,
                data={
                    "tenant_id": grant["scope"]["tenant_id"],
                    "grant_id": grant["grant_id"],
                    "grant_version": grant["grant_version"],
                    "plan_id": grant["plan_id"],
                    "episode_id": episode_id,
                    "record_kind": kind,
                    **data,
                },
                idempotency=key,
            ), actor)

    def _attempt_count(self, grant: dict[str, Any], episode_id: str) -> int:
        with self.scope.environment(PROJECT):
            rows = self.entries.supervisor_records(
                "SupervisorEpisode", last=100, tenant_id=grant["scope"]["tenant_id"],
                grant_id=grant["grant_id"], episode_id=episode_id, record_kind="attempt",
            )
        return len(rows)

    def _attempt_key(self, grant: dict[str, Any], episode_id: str, attempt_id: str) -> str:
        return f"supervisor:episode-attempt:{grant['scope']['tenant_id']}:{grant['grant_id']}:{episode_id}:{attempt_id}"

    def _qualification_key(self, grant: dict[str, Any], episode_id: str, observation_id: str) -> str:
        return f"supervisor:episode-qualification:{grant['scope']['tenant_id']}:{grant['grant_id']}:{episode_id}:{observation_id}"

    def _escalation_key(self, grant: dict[str, Any], episode_id: str) -> str:
        return f"supervisor:episode-escalation:{grant['scope']['tenant_id']}:{grant['grant_id']}:{episode_id}"

    def _current_epoch(self, grant: dict[str, Any]) -> int:
        with self.scope.environment(PROJECT):
            rows = self.entries.supervisor_records("SupervisorInstallation", last=1, tenant_id=grant["scope"]["tenant_id"])
        return int(rows[0].data["epoch"]) if rows else grant["scope"]["installation_epoch"]

    @staticmethod
    def _attempt_result(row: Entry, duplicate: bool) -> dict[str, Any]:
        return {"status": row.data["status"], "reason": row.data["reason"], "attempt_count": row.data["attempt_count"], "duplicate": duplicate}

    @staticmethod
    def _identifier(value: object) -> bool:
        return isinstance(value, str) and 1 <= len(value) <= 256
