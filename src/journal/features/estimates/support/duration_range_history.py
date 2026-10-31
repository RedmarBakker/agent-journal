from datetime import datetime
import hashlib
import json


class DurationRangeHistory:
    """Projects immutable task outcome rows into separate elapsed duration observations."""

    def observations(self, histories: list[dict], as_of: float) -> list[dict]:
        return [row for history in histories for task in history.get("tasks", ())
                for row in self.task_observations(history, task, as_of)]

    @staticmethod
    def input_cut(observations: list[dict], as_of: float) -> str:
        encoded = json.dumps({"as_of": as_of, "observations": observations}, sort_keys=True,
                             separators=(",", ":"), default=str).encode()
        return hashlib.sha256(encoded).hexdigest()

    def task_observations(self, history: dict, task: dict, as_of: float) -> list[dict]:
        facts = self.facts(task.get("outcomes", ()), as_of)
        starts = [row for row in facts if row["kind"] == "task_started"]
        if not starts:
            return []
        reopen = max((row["occurred_at"] for row in facts if row["kind"] == "task_reopened"), default=0.0)
        start = next((row for row in reversed(starts) if row["occurred_at"] > reopen), None)
        if start is None or self.cancelled_after(facts, start["occurred_at"]):
            return []
        cohort = self.cohort(history, start)
        changed = self.cohort_changed(facts, start, cohort)
        size = self.size(start)
        completed = [row for row in facts if row["kind"] in ("task_completed", "worker_work_merged")
                     and row["occurred_at"] >= start["occurred_at"]]
        completion = max(completed, key=lambda row: row["occurred_at"]) if completed else None
        execution_end = completion["occurred_at"] if completion else as_of
        output = [self.observation(task, cohort, size, "execution_cycle", start["occurred_at"], execution_end,
                                   completion is None, changed)]
        if completion:
            delivery = self.delivery_completion(task, facts, completion["occurred_at"])
            delivery_end = delivery["occurred_at"] if delivery else as_of
            if delivery_end > completion["occurred_at"]:
                output.append(self.observation(task, cohort, size, "delivery_delay", completion["occurred_at"],
                                               delivery_end, delivery is None, changed))
        return output

    @classmethod
    def facts(cls, rows, as_of: float) -> list[dict]:
        output = []
        for row in rows:
            moment = cls.moment(row.get("occurred_at"))
            if moment is None or moment > as_of:
                continue
            output.append({**row, "occurred_at": moment})
        return sorted(output, key=lambda row: (row["occurred_at"], row.get("id", 0)))

    @classmethod
    def cohort(cls, history: dict, start: dict) -> dict:
        dimensions = start.get("cohort_dimensions") or {}
        environment_id = dimensions.get("environment_id", history.get("scope", {}).get("environment_id"))
        return {"environment_id": environment_id, "domain": dimensions.get("domain"),
                "size_scale_version": dimensions.get("size_scale_version"),
                "criteria_version": dimensions.get("criteria_version"), "model": dimensions.get("model"),
                "tier": dimensions.get("tier"), "cohort_version": start.get("cohort_version")}

    @classmethod
    def cohort_changed(cls, facts: list[dict], start: dict, cohort: dict) -> bool:
        later = [row for row in facts if row["occurred_at"] >= start["occurred_at"]
                 and row.get("cohort_dimensions") is not None]
        return any(cls.cohort_dimensions(row) != cohort for row in later)

    @staticmethod
    def cohort_dimensions(row: dict) -> dict:
        dimensions = row.get("cohort_dimensions") or {}
        return {"environment_id": dimensions.get("environment_id"), "domain": dimensions.get("domain"),
                "size_scale_version": dimensions.get("size_scale_version"),
                "criteria_version": dimensions.get("criteria_version"), "model": dimensions.get("model"),
                "tier": dimensions.get("tier"), "cohort_version": row.get("cohort_version")}

    @staticmethod
    def size(start: dict) -> int | None:
        value = start.get("committed_size")
        return value if value is not None else start.get("planned_size")

    @classmethod
    def delivery_completion(cls, task: dict, facts: list[dict], after: float) -> dict | None:
        evidence_id = (task.get("delivery") or {}).get("evidence_id")
        return next((row for row in reversed(facts) if row["occurred_at"] >= after
                     and row["kind"] in ("delivery_accepted", "delivery_corrected")
                     and row.get("details", {}).get("delivery_id") == evidence_id), None)

    @staticmethod
    def cancelled_after(facts: list[dict], start: float) -> bool:
        return any(row["kind"] == "task_cancelled" and row["occurred_at"] >= start for row in facts)

    @staticmethod
    def observation(task: dict, cohort: dict, size: int | None, stage: str, start: float, end: float,
                    right_censored: bool, cohort_changed: bool) -> dict:
        return {"task_id": task.get("task_id"), "stage": stage, "cohort": cohort, "size_points": size,
                "duration_seconds": max(0.0, end - start), "observed_at": end,
                "right_censored": right_censored, "cohort_changed": cohort_changed,
                "wait_accounting": "elapsed stage time includes waits"}

    @staticmethod
    def moment(value: object) -> float | None:
        if not isinstance(value, str) or not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
