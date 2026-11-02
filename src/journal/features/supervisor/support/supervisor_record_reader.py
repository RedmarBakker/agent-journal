from collections import Counter
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from journal.features.supervisor.support.supervisor_capabilities import (
    AREA_DEFINITIONS, AREA_KEYS, CAPABILITY_CATALOGUE,
)
from journal.features.supervisor.support.supervisor_episode_qualification import OBSERVATION_ENTRY
from journal.features.supervisor.support.supervisor_maintenance import OPERATION_COMMANDS
from journal.features.supervisor.support.supervisor_wakeups import RESULTS, WAKEUP_ENTRY
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
AREA_TITLES = {key: title for key, title, *_ in AREA_DEFINITIONS}
AREA_KEYS_BY_TITLE = {title: key for key, title in AREA_TITLES.items()}
CAPABILITY_TITLES = {
    capability: label
    for _key, _title, verbs, _displayed, _note in AREA_DEFINITIONS
    for capability, label, _tier in verbs
}
TIER_NUMBERS = {"tier 1": 1, "tier 2": 2, "tier 3": 3}


class SupervisorRecordReader:
    """Reads supervisor wake-ups, runs and receipts for plans in the current environment."""

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

    def history(self, plan: str, area: str, tier: str, result: str, before: str) -> dict[str, Any]:
        plan_ids = self._plan_ids(plan)
        self._area(area)
        tier_number = self._tier(tier)
        self._result(result)
        history_cursor = self._history_cursor(before)
        with self.scope.environment(PROJECT):
            runs, receipts = self._records(plan_ids)
            history_rows = self._history_rows(plan_ids, runs, receipts, area, tier_number, result)
            history, next_before = self._history_page(history_rows, history_cursor)
        return {"areas": sorted(AREAS), "history": history, "next_before": next_before}

    def costs(self) -> dict[str, Any]:
        now = self.time_source.moment()
        plan_ids = self._plan_ids("")
        plan_titles = {plan_id: self.plans.find(plan_id).title for plan_id in plan_ids}
        with self.scope.environment(PROJECT):
            runs, receipts = self._records(plan_ids)
            rows = self._history_source_rows(plan_ids, runs, receipts)
            outcomes = [report for receipt in receipts for report in self._entries(
                "SupervisorActionReport", receipt_id=receipt.row_id, report_kind="outcome",
            )]
        return self._cost_summary(now, rows, plan_titles, outcomes)

    @staticmethod
    def _tier(tier: str) -> int | None:
        if not tier:
            return None
        if tier not in {"1", "2", "3"}:
            raise SupervisorFailure(400, "the supervisor records tier is invalid")
        return int(tier)

    @staticmethod
    def _result(result: str) -> None:
        if result and result not in RESULTS | {"In progress"}:
            raise SupervisorFailure(400, "the supervisor records result is invalid")

    @staticmethod
    def _history_cursor(cursor: str) -> tuple[int, int] | None:
        if not cursor:
            return None
        parts = cursor.split(":")
        if len(parts) != 2 or any(not part.isdigit() for part in parts) or int(parts[1]) < 1:
            raise SupervisorFailure(400, "the supervisor history cursor is invalid")
        return int(parts[0]), int(parts[1])

    def _history_rows(self, plan_ids: list[int], runs: list[Entry], receipts: list[Entry], area: str,
                      tier: int | None, result: str) -> list[dict[str, Any]]:
        rows = self._history_source_rows(plan_ids, runs, receipts)
        rows = [row for row in rows if self._history_matches(row, area, tier, result)]
        return self._fold_quiet(rows)

    def _history_source_rows(self, plan_ids: list[int], runs: list[Entry],
                             receipts: list[Entry]) -> list[dict[str, Any]]:
        wakeups = [row for plan_id in plan_ids for row in self._entries(WAKEUP_ENTRY, plan_id=plan_id)]
        observations = [row for plan_id in plan_ids for row in self._entries(OBSERVATION_ENTRY, plan_id=plan_id)]
        tenants = {str(run.data.get("tenant_id")) for run in runs if run.data.get("tenant_id")}
        usage = [row for tenant in tenants for row in self._entries("SupervisorUsage", tenant_id=tenant)]
        undo_reports = [row for plan_id in plan_ids for row in self._entries(
            "SupervisorActionReport", plan_id=plan_id, report_kind="owner_undo",
        )]
        observation_by_id = {
            (row.data.get("tenant_id"), row.data.get("observation_id")): row for row in observations
        }
        usage_by_run = {(row.data.get("tenant_id"), row.data.get("run_ref")): row for row in usage}
        undone_receipts = {row.data.get("receipt_id") for row in undo_reports}
        runs_by_wakeup = {
            (run.data.get("tenant_id"), run.data.get("wakeup_id")): run
            for run in sorted(runs, key=lambda row: (row.created_at, row.row_id))
            if run.data.get("wakeup_id")
        }
        paired_runs = set()
        rows = []
        for wakeup in wakeups:
            run = runs_by_wakeup.get((wakeup.data.get("tenant_id"), wakeup.data.get("wakeup_id")))
            if run:
                paired_runs.add(run.row_id)
            rows.append(self._history_row(wakeup, run, receipts, observation_by_id, usage_by_run, undone_receipts))
        rows.extend(
            self._history_row(None, run, receipts, observation_by_id, usage_by_run, undone_receipts)
            for run in runs if run.row_id not in paired_runs
        )
        return rows

    def _history_row(self, wakeup: Entry | None, run: Entry | None, receipts: list[Entry],
                     observations: dict[tuple[object, object], Entry], usage: dict[tuple[object, object], Entry],
                     undone_receipts: set[object]) -> dict[str, Any]:
        receipt_rows = self._for_run(run, receipts) if run else []
        actions = [
            action
            for receipt in receipt_rows
            for action in self._actions(receipt, undone_receipts)
        ]
        run_data = run.data if run else {}
        wakeup_data = wakeup.data if wakeup else {}
        result = wakeup_data.get("result") or self._run_result(receipt_rows)
        observation_ids = run_data.get("observation_ids", [])
        if not isinstance(observation_ids, list):
            observation_ids = []
        evidence = [observations.get((run_data.get("tenant_id"), observation_id))
                    for observation_id in observation_ids] if run else []
        moment = run.created_at if run else wakeup.created_at
        return {
            "id": wakeup.row_id if wakeup else run.row_id,
            "created_at": moment.isoformat(),
            "plan_id": wakeup_data.get("plan_id", run_data.get("plan_id")),
            "woken_by": self._woken_by(wakeup_data, run_data),
            "result": result,
            "what_saw": self._what_saw(evidence, result),
            "what_chose": "; ".join(dict.fromkeys(action["title"] for action in actions)) or result,
            "why": self._why(receipt_rows, wakeup_data),
            "cost": self._cost(run, usage),
            "actions": actions,
            "_has_run": run is not None,
            "_has_wakeup": wakeup is not None,
            "_moment": moment,
            "_sort_ms": self._created_ms(moment),
            "_sort_id": wakeup.row_id if wakeup else run.row_id,
        }

    def _actions(self, receipt: Entry, undone_receipts: set[object]) -> list[dict[str, Any]]:
        data = receipt.data
        operations = data.get("proposed_operations", [])
        commands = data.get("command_receipts", [])
        if not isinstance(operations, list):
            return []
        return [
            self._action(receipt, operation, index, commands, undone_receipts)
            for index, operation in enumerate(operations)
            if isinstance(operation, dict) and operation.get("kind") in OPERATION_COMMANDS
        ]

    def _action(self, receipt: Entry, operation: dict[str, Any], index: int, commands: object,
                undone_receipts: set[object]) -> dict[str, Any]:
        area, noun, verb = OPERATION_COMMANDS[operation["kind"]]
        capability = f"{noun} {verb}"
        area_key, capability_tier = CAPABILITY_CATALOGUE.get(capability, (AREA_KEYS_BY_TITLE.get(area), 3))
        command = commands[index] if isinstance(commands, list) and index < len(commands) else {}
        if not isinstance(command, dict):
            command = {}
        area = command.get("area", area)
        area_key = AREA_KEYS_BY_TITLE.get(area, area_key)
        tier = TIER_NUMBERS.get(str(command.get("tier", "")).lower(), capability_tier)
        status = command.get("status", receipt.data.get("status", "unknown"))
        changes = self._action_changes(receipt, operation, command, len(receipt.data.get("proposed_operations", [])))
        reversible = (status == "applied" and tier == 1 and bool(changes)
                      and command.get("readback_verification") == "verified")
        return {
            "area": area,
            "area_key": area_key,
            "title": CAPABILITY_TITLES.get(capability, capability),
            "tier": tier,
            "status": status,
            "receipt_id": receipt.row_id,
            "receipt_status": receipt.data.get("status", "unknown"),
            "reason": receipt.data.get("reason"),
            "changes": changes,
            "undo_available": reversible and receipt.row_id not in undone_receipts,
        }

    @staticmethod
    def _action_changes(receipt: Entry, operation: dict[str, Any], command: dict[str, Any],
                        count: int) -> list[dict[str, Any]]:
        rows = command.get("rows_changed", [])
        result = [
            {"field": change.get("field", change.get("event", "change")),
             "before": change.get("before", change.get("before_value")),
             "after": change.get("after", change.get("after_value"))}
            for change in rows if isinstance(change, dict)
        ] if isinstance(rows, list) else []
        fields = {
            "plan_priorities": {"priorities"},
            "diagnostic_task": {"plan_link", "phase_link"},
            "check_interval": {"interval"},
        }.get(operation.get("kind"), set())
        receipt_changes = receipt.data.get("changes", [])
        if isinstance(receipt_changes, list):
            for change in receipt_changes:
                if (isinstance(change, dict) and (count == 1 or change.get("field") in fields)
                        and not any(item["field"] == change.get("field") for item in result)):
                    result.append({"field": change.get("field", "change"),
                                   "before": change.get("before_value"), "after": change.get("after_value")})
        return result

    @staticmethod
    def _run_result(receipts: list[Entry]) -> str:
        if not receipts:
            return "In progress"
        statuses = {receipt.data.get("status") for receipt in receipts}
        if "applied" in statuses:
            return "Acted"
        if "proposed" in statuses:
            return "Proposed"
        if statuses.intersection({"conflicted", "rejected"}):
            return "Handed to you"
        return "In progress"

    @staticmethod
    def _woken_by(wakeup: dict[str, Any], run: dict[str, Any]) -> str:
        kind = wakeup.get("kind", run.get("kind", ""))
        source = run.get("source", "")
        if kind == "scheduled" or source in {"schedule", "scheduled", "timer"}:
            return "Schedule"
        event = str(kind or source or "event").replace("_", " ").capitalize()
        return f"Event: {event}"

    @staticmethod
    def _what_saw(observations: list[Entry | None], result: str) -> str:
        found = []
        for entry in observations:
            if entry is None:
                continue
            observation = entry.data.get("observation", {})
            facts = observation.get("facts", {}) if isinstance(observation, dict) else {}
            if not isinstance(facts, dict):
                continue
            check_id = facts.get("check_id")
            verdict = facts.get("verdict")
            output = facts.get("output_excerpt", "")
            summary = f"Check {check_id} {verdict}: {output}" if check_id and verdict else str(output)
            if summary:
                found.append(summary.rstrip(" .") + ".")
        if found:
            return "; ".join(dict.fromkeys(found))
        return "No relevant changes were found." if result == "Skipped as quiet" else "No observation was recorded."

    @staticmethod
    def _why(receipts: list[Entry], wakeup: dict[str, Any]) -> str:
        reasons = [str(receipt.data.get("rationale") or receipt.data.get("reason") or "").strip()
                   for receipt in receipts]
        reasons = [reason for reason in reasons if reason]
        if reasons:
            return "; ".join(dict.fromkeys(reasons))
        reason = str(wakeup.get("skip_reason", "")).strip()
        return {
            "quiet": "No relevant changes were found.",
            "empty": "No actionable change was found.",
            "busy": "Another wake-up was still running.",
            "evidence stale": "The saved evidence was out of date.",
            "budget used up": "The daily budget was used up.",
            "needs owner": "This wake-up needs your decision.",
        }.get(reason, reason or "No reason was recorded.")

    @staticmethod
    def _cost(run: Entry | None, usage: dict[tuple[object, object], Entry]) -> dict[str, Any]:
        if run is None:
            return {"status": "known", "usd": "0.00"}
        row = usage.get((run.data.get("tenant_id"), run.data.get("run_ref")))
        data = row.data if row else {}
        cost = data.get("cost_usd")
        if data.get("status") in {"known", "overrun"} and isinstance(cost, str) and cost:
            return {"status": data["status"], "usd": cost}
        return {"status": "unknown", "usd": None}

    @staticmethod
    def _history_matches(row: dict[str, Any], area: str, tier: int | None, result: str) -> bool:
        actions = row["actions"]
        return ((not area or any(action["area_key"] == area for action in actions))
                and (tier is None or any(action["tier"] == tier for action in actions))
                and (not result or row["result"] == result))

    def _fold_quiet(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        quiet = [row for row in rows if row["result"] == "Skipped as quiet"]
        if not quiet:
            return rows
        newest = max(quiet, key=self._history_sort_key)
        plan_ids = {row["plan_id"] for row in quiet}
        return [row for row in rows if row["result"] != "Skipped as quiet"] + [{
            "id": newest["id"], "created_at": newest["created_at"],
            "plan_id": next(iter(plan_ids)) if len(plan_ids) == 1 else None,
            "woken_by": "Quiet wake-ups", "result": "Skipped as quiet",
            "what_saw": "No relevant changes were found.", "what_chose": "Skip this wake-up.",
            "why": "No relevant changes were found.", "cost": {"status": "known", "usd": "0.00"},
            "actions": [], "quiet_count": len(quiet),
            "quiet_since": min(row["created_at"] for row in quiet),
            "_sort_ms": newest["_sort_ms"], "_sort_id": newest["_sort_id"],
        }]

    @staticmethod
    def _history_sort_key(row: dict[str, Any]) -> tuple[int, int]:
        return row["_sort_ms"], row["_sort_id"]

    @staticmethod
    def _created_ms(moment: datetime) -> int:
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return int(moment.timestamp() * 1000)

    def _history_page(self, rows: list[dict[str, Any]], before: tuple[int, int] | None
                      ) -> tuple[list[dict[str, Any]], str | None]:
        ordered = sorted(rows, key=self._history_sort_key, reverse=True)
        remaining = [row for row in ordered if before is None or self._history_sort_key(row) < before]
        page = remaining[:PAGE_SIZE]
        next_before = None
        if len(remaining) > PAGE_SIZE:
            newest = page[-1]
            next_before = f"{newest['_sort_ms']}:{newest['_sort_id']}"
        return [{key: value for key, value in row.items() if not key.startswith("_")} for row in page], next_before

    def _cost_summary(self, now: datetime, rows: list[dict[str, Any]], plan_titles: dict[int, str],
                      outcomes: list[Entry]) -> dict[str, Any]:
        useful_receipts = {row.data.get("receipt_id") for row in outcomes
                           if row.data.get("outcome") == "useful_evidence"}
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week = now - timedelta(days=7)
        month = now - timedelta(days=30)
        periods = {
            "today": self._cost_period(rows, today, now + timedelta(microseconds=1), useful_receipts, 1),
            "week": self._cost_period(rows, week, now + timedelta(microseconds=1), useful_receipts, 7),
            "month": self._cost_period(rows, month, now + timedelta(microseconds=1), useful_receipts, 30),
        }
        week_rows = self._cost_run_rows(rows, week, now + timedelta(microseconds=1))
        average_cost = Decimal(periods["week"]["known_usd"])
        average_run = self._average(average_cost, periods["week"]["known_runs"])
        quiet_count = sum(row["result"] == "Skipped as quiet" for row in rows
                          if row["_has_wakeup"] and week <= row["_moment"] <= now)
        savings = self._amount(Decimal(average_run) * quiet_count) if average_run is not None else None
        return {
            "periods": periods,
            "averages": {
                "per_wakeup": {"usd": average_run, "known_runs": periods["week"]["known_runs"],
                               "unknown_runs": periods["week"]["unknown_runs"]},
                "per_action": {"usd": self._average(average_cost, periods["week"]["known_actions"]),
                               "known_actions": periods["week"]["known_actions"],
                               "unknown_runs": periods["week"]["unknown_runs"]},
                "per_useful_result": {
                    "usd": self._average(Decimal(periods["week"]["useful_known_usd"]),
                                         periods["week"]["known_useful_results"]),
                    "known_results": periods["week"]["known_useful_results"],
                    "unknown_results": periods["week"]["unknown_useful_results"],
                },
            },
            "per_plan": self._cost_by_plan(week_rows, plan_titles),
            "per_area": self._cost_by_area(week_rows),
            "quiet_savings": {"quiet_wakeups": quiet_count, "estimated_usd": savings},
            "wakeups_per_day": self._wakeups_per_day(rows, now.date()),
            "daily_trend": self._daily_trend(rows, now.date()),
        }

    def _cost_period(self, rows: list[dict[str, Any]], start: datetime, end: datetime,
                     useful_receipts: set[object], days: int) -> dict[str, Any]:
        wakeups = [row for row in rows if (row["_has_wakeup"] or row["_has_run"])
                   and start <= row["_moment"] < end]
        runs = [row for row in wakeups if row["_has_run"]]
        known = [row for row in runs if row["cost"]["status"] != "unknown"]
        unknown = [row for row in runs if row["cost"]["status"] == "unknown"]
        known_cost = sum((Decimal(row["cost"]["usd"]) for row in known), Decimal(0))
        known_action_count = sum(len(row["actions"]) for row in known)
        known_useful = self._useful_receipt_ids(known, useful_receipts)
        unknown_useful = self._useful_receipt_ids(unknown, useful_receipts)
        useful_cost = sum((Decimal(row["cost"]["usd"]) for row in known
                           if any(action["receipt_id"] in known_useful for action in row["actions"])), Decimal(0))
        return {
            "days": days,
            "known_usd": self._amount(known_cost),
            "unknown_runs": len(unknown),
            "runs": len(runs),
            "known_runs": len(known),
            "wakeups": len(wakeups),
            "known_actions": known_action_count,
            "known_useful_results": len(known_useful),
            "unknown_useful_results": len(unknown_useful),
            "useful_known_usd": self._amount(useful_cost),
        }

    @staticmethod
    def _useful_receipt_ids(rows: list[dict[str, Any]], useful_receipts: set[object]) -> set[object]:
        return {action["receipt_id"] for row in rows for action in row["actions"]
                if action["receipt_id"] in useful_receipts}

    @staticmethod
    def _cost_run_rows(rows: list[dict[str, Any]], start: datetime, end: datetime) -> list[dict[str, Any]]:
        return [row for row in rows if row["_has_run"] and start <= row["_moment"] < end]

    def _cost_by_plan(self, rows: list[dict[str, Any]], plan_titles: dict[int, str]) -> list[dict[str, Any]]:
        totals: dict[int, dict[str, Any]] = {}
        for row in rows:
            plan_id = row["plan_id"]
            total = totals.setdefault(plan_id, {"known": Decimal(0), "unknown": 0})
            if row["cost"]["status"] == "unknown":
                total["unknown"] += 1
            else:
                total["known"] += Decimal(row["cost"]["usd"])
        return [
            {"plan_id": plan_id, "title": plan_titles[plan_id], "known_usd": self._amount(total["known"]),
             "unknown_runs": total["unknown"]}
            for plan_id, total in sorted(totals.items(), key=lambda item: (-item[1]["known"], item[0]))
        ]

    def _cost_by_area(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        totals: dict[str, dict[str, Any]] = {}
        for row in rows:
            actions = row["actions"] or [{"area_key": "whole-environment", "area": "Whole environment"}]
            if row["cost"]["status"] == "unknown":
                for action in {item["area_key"]: item for item in actions}.values():
                    total = totals.setdefault(action["area_key"], {
                        "title": action["area"], "known": Decimal(0), "unknown": 0,
                    })
                    total["unknown"] += 1
                continue
            share = Decimal(row["cost"]["usd"]) / len(actions)
            for action in actions:
                total = totals.setdefault(action["area_key"], {
                    "title": action["area"], "known": Decimal(0), "unknown": 0,
                })
                total["known"] += share
        return [
            {"area_key": area, "title": total["title"], "known_usd": self._amount(total["known"]),
             "unknown_runs": total["unknown"]}
            for area, total in sorted(totals.items(), key=lambda item: (-item[1]["known"], item[0]))
        ]

    def _wakeups_per_day(self, rows: list[dict[str, Any]], today: date) -> list[dict[str, Any]]:
        counts: dict[date, dict[str, int]] = {}
        for row in rows:
            if not row["_has_wakeup"] and not row["_has_run"]:
                continue
            day = row["_moment"].date()
            if today - timedelta(days=6) <= day <= today:
                count = counts.setdefault(day, {"total": 0, "quiet": 0})
                count["total"] += 1
                count["quiet"] += row["result"] == "Skipped as quiet"
        return [
            {"date": (today - timedelta(days=offset)).isoformat(),
             **counts.get(today - timedelta(days=offset), {"total": 0, "quiet": 0})}
            for offset in range(6, -1, -1)
        ]

    def _daily_trend(self, rows: list[dict[str, Any]], today: date) -> list[dict[str, Any]]:
        totals: dict[date, dict[str, Any]] = {}
        for row in rows:
            if not row["_has_run"]:
                continue
            day = row["_moment"].date()
            if today - timedelta(days=29) <= day <= today:
                total = totals.setdefault(day, {"known": Decimal(0), "unknown": 0})
                if row["cost"]["status"] == "unknown":
                    total["unknown"] += 1
                else:
                    total["known"] += Decimal(row["cost"]["usd"])
        trend = []
        for offset in range(29, -1, -1):
            day = today - timedelta(days=offset)
            total = totals.get(day, {"known": Decimal(0), "unknown": 0})
            trend.append({"date": day.isoformat(),
                          "known_usd": None if total["unknown"] else self._amount(total["known"]),
                          "unknown_runs": total["unknown"]})
        return trend

    @staticmethod
    def _amount(amount: Decimal) -> str:
        return format(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")

    @classmethod
    def _average(cls, amount: Decimal, count: int) -> str | None:
        return cls._amount(amount / count) if count else None

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
