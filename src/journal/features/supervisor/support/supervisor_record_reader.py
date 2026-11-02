from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from journal.features.supervisor.support.supervisor_capabilities import AREA_KEYS
from journal.models.entry import Entry
from journal.repositories.entries import Entries
from journal.repositories.plans import Plans
from journal.repositories.scope import PROJECT, Scope
from journal.support.time_source import TimeSource
from journal.supervisor_failure import SupervisorFailure

PAGE_SIZE = 100
RECEIPT_STATUSES = ("applied", "conflicted", "proposed", "rejected")
OPERATION_AREAS = {
    "diagnostic_task": "plans-and-tasks",
    "plan_priorities": "plans-and-tasks",
    "check_interval": "checks",
}
AREAS = frozenset(AREA_KEYS)


class SupervisorRecordReader:
    """Reads the supervisor runs and receipts for plans in the current environment."""

    def __init__(self, entries: Entries, plans: Plans, scope: Scope, time_source: TimeSource) -> None:
        self.entries, self.plans, self.scope, self.time_source = entries, plans, scope, time_source

    def read(self, period: str, plan: str, area: str, before: str) -> dict[str, Any]:
        plan_ids = self._plan_ids(plan)
        self._area(area)
        before_id = self._before_id(before)
        current, previous = self._windows(period, self.time_source.moment())
        with self.scope.environment(PROJECT):
            runs, receipts = self._records(plan_ids)
            verified = self._verified_receipts(receipts)
        current_receipts = [receipt for receipt in receipts if self._within(receipt.created_at, current)
                            and self._receipt_matches_area(receipt, area)]
        previous_receipts = [receipt for receipt in receipts if self._within(receipt.created_at, previous)
                             and self._receipt_matches_area(receipt, area)]
        current_runs = [run for run in runs if self._within(run.created_at, current)
                        and self._run_matches_area(run, current_receipts, area)]
        previous_runs = [run for run in runs if self._within(run.created_at, previous)
                         and self._run_matches_area(run, previous_receipts, area)]
        record_rows = self._record_rows(current_runs, current_receipts, verified)
        remaining = [row for row in record_rows if before_id is None or row["id"] < before_id]
        page = remaining[:PAGE_SIZE]
        return {
            "areas": sorted(AREAS),
            "current": self._summary(current_runs, current_receipts, verified),
            "previous": self._summary(previous_runs, previous_receipts, verified),
            "records": page,
            "next_before": page[-1]["id"] if len(remaining) > PAGE_SIZE else None,
        }

    def _plan_ids(self, plan: str) -> list[int]:
        if not plan:
            ids = []
            previous = None
            while True:
                page = self.plans.page(PAGE_SIZE, previous)
                ids.extend(row.row_id for row in page)
                if len(page) < PAGE_SIZE:
                    return ids
                previous = page[-1].row_id
        if not plan.isdigit() or int(plan) < 1:
            raise SupervisorFailure(400, "the supervisor records plan is invalid")
        plan_id = int(plan)
        self.plans.find(plan_id)
        return [plan_id]

    @staticmethod
    def _area(area: str) -> None:
        if area and area not in AREAS:
            raise SupervisorFailure(400, "the supervisor records area is invalid")

    @staticmethod
    def _before_id(before: str) -> int | None:
        if not before:
            return None
        if not before.isdigit() or int(before) < 1:
            raise SupervisorFailure(400, "the supervisor records cursor is invalid")
        return int(before)

    def _windows(self, period: str, now: datetime) -> tuple[tuple[datetime, datetime], tuple[datetime, datetime]]:
        if period == "today":
            current_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            previous_start = current_start - timedelta(days=1)
        elif period in ("last_7_days", "last_30_days"):
            days = 7 if period == "last_7_days" else 30
            current_start = now - timedelta(days=days)
            previous_start = current_start - timedelta(days=days)
        else:
            raise SupervisorFailure(400, "the supervisor records period is invalid")
        current_end = now + timedelta(microseconds=1)
        return (current_start, current_end), (previous_start, current_start)

    def _records(self, plan_ids: list[int]) -> tuple[list[Entry], list[Entry]]:
        runs = [run for plan_id in plan_ids for run in self._entries("SupervisorRun", plan_id=plan_id)]
        receipts = []
        for run in runs:
            run_ref = run.data.get("run_ref")
            tenant_id, grant_id = run.data.get("tenant_id"), run.data.get("grant_id")
            if not isinstance(run_ref, str) or not isinstance(tenant_id, str) or not isinstance(grant_id, str):
                continue
            receipts.extend(self._entries("SupervisorActionReceipt", tenant_id=tenant_id,
                                          grant_id=grant_id, run_id=run_ref))
        return runs, list({receipt.row_id: receipt for receipt in receipts}.values())

    def _verified_receipts(self, receipts: list[Entry]) -> set[int]:
        return {
            receipt.row_id for receipt in receipts
            if receipt.data.get("status") == "applied" and any(report.data.get("verification") == "verified"
                   for report in self._entries("SupervisorActionReport", receipt_id=receipt.row_id,
                                                report_kind="verification"))
        }

    def _entries(self, entry_type: str, **filters) -> list[Entry]:
        found = []
        after_id = 0
        while True:
            page = self.entries.supervisor_page(entry_type, PAGE_SIZE, after_id, **filters)
            found.extend(page)
            if len(page) < PAGE_SIZE:
                return found
            after_id = page[-1].row_id

    def _run_matches_area(self, run: Entry, receipts: list[Entry], area: str) -> bool:
        return not area or any(self._receipt_matches_area(receipt, area)
                               for receipt in self._for_run(run, receipts))

    @staticmethod
    def _for_run(run: Entry, receipts: list[Entry]) -> list[Entry]:
        key = (run.data.get("tenant_id"), run.data.get("grant_id"), run.data.get("run_ref"))
        return [receipt for receipt in receipts
                if (receipt.data.get("tenant_id"), receipt.data.get("grant_id"),
                    receipt.data.get("run_id")) == key]

    def _receipt_matches_area(self, receipt: Entry, area: str) -> bool:
        return not area or any(OPERATION_AREAS.get(kind) == area for kind in self._operation_kinds(receipt))

    @staticmethod
    def _operation_kinds(receipt: Entry) -> list[str]:
        operations = receipt.data.get("proposed_operations", [])
        if not isinstance(operations, list):
            return []
        return [operation["kind"] for operation in operations
                if isinstance(operation, dict) and isinstance(operation.get("kind"), str)]

    @staticmethod
    def _within(moment: datetime, window: tuple[datetime, datetime]) -> bool:
        return window[0] <= moment < window[1]

    def _summary(self, runs: list[Entry], receipts: list[Entry], verified: set[int]) -> dict[str, Any]:
        statuses = {status: 0 for status in RECEIPT_STATUSES}
        statuses.update(Counter(str(receipt.data.get("status", "unknown")) for receipt in receipts))
        return {"runs": len(runs), "receipts": statuses,
                "verified_receipts": sum(receipt.row_id in verified for receipt in receipts)}

    @staticmethod
    def _record_rows(runs: list[Entry], receipts: list[Entry], verified: set[int]) -> list[dict[str, Any]]:
        plans_by_run = {
            (run.data.get("tenant_id"), run.data.get("grant_id"), run.data.get("run_ref")): run.data.get("plan_id")
            for run in runs
        }
        rows = [
            {"id": run.row_id, "kind": "run", "created_at": run.created_at.isoformat(),
             "plan_id": run.data.get("plan_id"), "run_ref": run.data.get("run_ref"),
             "source": run.data.get("source"), "status": run.data.get("status")}
            for run in runs
        ]
        rows.extend(
            {"id": receipt.row_id, "kind": "receipt", "created_at": receipt.created_at.isoformat(),
             "action_id": receipt.data.get("action_id"), "run_id": receipt.data.get("run_id"),
             "plan_id": plans_by_run.get((receipt.data.get("tenant_id"), receipt.data.get("grant_id"),
                                           receipt.data.get("run_id"))),
             "status": receipt.data.get("status"), "reason": receipt.data.get("reason"),
             "verification": "verified" if receipt.row_id in verified else "unverified",
             "operations": receipt.data.get("proposed_operations", [])}
            for receipt in receipts
        )
        return sorted(rows, key=lambda row: row["id"], reverse=True)
