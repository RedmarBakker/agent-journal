from datetime import datetime
from typing import Any

from journal.models.entry import Entry
from journal.repositories.entries import Entries
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.support.actor import Actor
from journal.supervisor_authority import SUPERVISOR_ACTOR, SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from journal.supervisor_principal import SupervisorPrincipal


class SupervisorWakeSchedule:
    """Tracks due scheduled supervisor wakes against the current grant interval."""

    def __init__(self, authority: SupervisorAuthority, entries: Entries, control_entries: SupervisorEntries,
                 scope: Scope) -> None:
        self.authority, self.entries, self.control_entries = authority, entries, control_entries
        self.scope = scope

    def interval_minutes(self, principal: SupervisorPrincipal) -> int:
        return self.authority.observation_permissions(principal).wake_interval_minutes

    def is_due(self, principal: SupervisorPrincipal, grant: dict[str, Any], interval_minutes: int,
               wake_at_ms: int) -> bool:
        last = self._last_wake(principal, grant)
        anchor = last.data.get("wake_at_ms") if last else self._grant_created_at(principal, grant)
        if type(anchor) is not int or anchor < 0:
            raise SupervisorFailure(403, "the supervisor scheduled wake time is invalid")
        return wake_at_ms - anchor >= interval_minutes * 60_000

    def record(self, principal: SupervisorPrincipal, grant: dict[str, Any], interval_minutes: int,
               wake_at_ms: int, cursor: str | None, result: dict[str, Any]) -> None:
        reason = result.get("reason", "")
        key = f"supervisor:wake:{grant['grant_id']}:scheduled:{wake_at_ms}"
        self.control_entries.recorded(Entry(
            environment_id=PROJECT,
            entry_type="SupervisorWake",
            actor=Actor.plugin(SUPERVISOR_ACTOR),
            data={
                "tenant_id": principal.scope["tenant_id"],
                "environment_id": principal.scope["environment_id"],
                "grant_id": grant["grant_id"],
                "grant_version": grant["grant_version"],
                "plan_id": grant["plan_id"],
                "wake_kind": "scheduled",
                "source": "timer",
                "interval_minutes": interval_minutes,
                "observation_cursor": cursor,
                "wake_at_ms": wake_at_ms,
                "status": result["status"],
                "reason": reason,
            },
            idempotency=key,
        ), Actor.plugin(SUPERVISOR_ACTOR))

    def _last_wake(self, principal: SupervisorPrincipal, grant: dict[str, Any]) -> Entry | None:
        with self.scope.environment(PROJECT):
            rows = self.entries.supervisor_records(
                "SupervisorWake", last=1,
                tenant_id=principal.scope["tenant_id"], grant_id=grant["grant_id"], wake_kind="scheduled",
            )
        return rows[0] if rows else None

    def _grant_created_at(self, principal: SupervisorPrincipal, grant: dict[str, Any]) -> int:
        with self.scope.environment(grant["driver_environment_id"]):
            rows = self.entries.supervisor_records(
                "SupervisorGrant", last=1,
                tenant_id=principal.scope["tenant_id"], grant_id=grant["grant_id"],
            )
        if not rows or not isinstance(rows[0].created_at, datetime):
            raise SupervisorFailure(403, "the supervisor grant schedule is unavailable")
        return int(rows[0].created_at.timestamp() * 1000)

