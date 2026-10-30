from datetime import date, timedelta
import hashlib
import json
import math
import random


MIN_DELIVERED_OUTCOMES = 10
MIN_CAPACITY_DAYS = 20
DEFAULT_TRIALS = 10000
DEFAULT_HORIZON_SPRINTS = 6
METHOD_VERSION = "baseline-throughput-v1"
ACCEPTED_DELIVERIES = ("delivery_accepted", "delivery_corrected")


class BaselineForecast:
    """A deterministic bootstrap simulation over comparable delivery and shared capacity blocks."""

    def estimate(self, source: dict) -> dict:
        input_cut = self.fingerprint(source)
        seed = self.seed(source, input_cut)
        calendar = source.get("calendar", {})
        as_of = self.day(source.get("as_of"))
        tasks, unknown_sizes, unknown_domains, unknown_cohorts = self.scope(source.get("scope", ()))
        unknown_scope = sorted({row for row in source.get("scope_uncertainties", ()) if isinstance(row, int)})
        cohorts = {task["cohort_key"] for task in tasks}
        outcomes = self.outcomes(source.get("accepted_deliveries", ()), cohorts)
        blocks, invalid_capacity = self.capacity_days(source.get("capacity_days", ()), as_of)
        counts = {key: len(outcomes.get(key, {})) for key in cohorts}
        missing = self.missing(counts, len(blocks), unknown_domains, unknown_sizes, unknown_cohorts, invalid_capacity)
        if unknown_scope:
            missing.append("approved scope")
        missing.extend(self.calendar_missing(calendar, as_of))
        missing = sorted(set(missing))
        prepared = self.prepared(tasks, counts, blocks, missing, unknown_domains, unknown_sizes, unknown_cohorts,
                                 unknown_scope, invalid_capacity, source, calendar, as_of, input_cut, seed)
        if missing:
            return self.abstention(prepared)
        trials = self.positive(source.get("trials"), DEFAULT_TRIALS)
        horizon = self.positive(source.get("horizon_sprints"), DEFAULT_HORIZON_SPRINTS)
        sprint_days = self.positive(calendar.get("sprint_length_days"), 14)
        simulations, batches = self.simulations(tasks, blocks, as_of, sprint_days * horizon, trials, seed, calendar)
        result = self.distribution(simulations, prepared, len(blocks))
        result["plan_forecasts"] = self.plan_distributions(simulations, prepared)
        result["sensitivity"] = self.sensitivity(batches, prepared)
        return result

    @staticmethod
    def cohort(cohort: dict) -> dict:
        dimensions = ("domain", "size_scale_version", "criteria_version", "model", "tier")
        return {key: cohort.get(key) for key in dimensions}

    @classmethod
    def cohort_key(cls, cohort: dict) -> str:
        return json.dumps(cls.cohort(cohort), sort_keys=True, separators=(",", ":"))

    @staticmethod
    def fingerprint(source: dict) -> str:
        encoded = json.dumps(source, sort_keys=True, separators=(",", ":"), default=str).encode()
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def seed(source: dict, input_cut: str) -> int:
        value = source.get("seed")
        return value if isinstance(value, int) and not isinstance(value, bool) else int(input_cut[:16], 16)

    @classmethod
    def scope(cls, rows) -> tuple[list[dict], list[int], list[int], list[int]]:
        tasks, unknown_sizes, unknown_domains, unknown_cohorts = [], [], [], []
        for row in rows:
            if not isinstance(row, dict) or row.get("delivery_status") in ("delivered", "removed"):
                continue
            task_id = row.get("task_id")
            points = row.get("size_points")
            cohort = row.get("cohort") or {}
            if not isinstance(points, int) or isinstance(points, bool) or points <= 0:
                unknown_sizes.append(task_id)
            missing = [name for name in ("domain", "size_scale_version", "criteria_version", "model", "tier") if not cohort.get(name)]
            if not cohort.get("domain"):
                unknown_domains.append(task_id)
            if missing:
                unknown_cohorts.append(task_id)
            if isinstance(points, int) and not isinstance(points, bool) and points > 0 and not missing and isinstance(task_id, int):
                tasks.append({**row, "size_points": points, "cohort_key": cls.cohort_key(cohort)})
        return tasks, sorted(set(unknown_sizes)), sorted(set(unknown_domains)), sorted(set(unknown_cohorts))

    @classmethod
    def outcomes(cls, rows, cohorts: set[str]) -> dict[str, dict[int, dict]]:
        accepted = {}
        for row in rows:
            if row.get("kind") not in ACCEPTED_DELIVERIES or row.get("current", True) is False:
                continue
            cohort_key = cls.cohort_key(row.get("cohort") or {})
            task_id = row.get("task_id")
            points = row.get("size_points")
            if (cohort_key not in cohorts or not isinstance(task_id, int) or not isinstance(points, int)
                    or isinstance(points, bool) or points <= 0):
                continue
            prior = accepted.setdefault(cohort_key, {}).get(task_id)
            if prior is None or row.get("generation", 1) >= prior.get("generation", 1):
                accepted[cohort_key][task_id] = row
        return accepted

    @classmethod
    def capacity_days(cls, rows, as_of: date | None) -> tuple[list[dict], bool]:
        days = {}
        invalid = False
        for row in rows:
            observed = cls.day(row.get("date")) if isinstance(row, dict) else None
            places = row.get("available_places") if isinstance(row, dict) else None
            batches_value = row.get("deployment_batches") if isinstance(row, dict) else None
            if (observed is None or as_of is None or observed > as_of or not isinstance(places, int)
                    or isinstance(places, bool) or places < 0 or not isinstance(batches_value, list)):
                invalid = True
                continue
            if observed in days:
                invalid = True
                continue
            batches = []
            for batch in batches_value:
                points = batch.get("points_by_cohort", {}) if isinstance(batch, dict) else {}
                values = {key: value for key, value in points.items() if isinstance(key, str) and isinstance(value, int)
                          and not isinstance(value, bool) and value > 0}
                if places == 0 and values:
                    invalid = True
                    batches = []
                    break
                if values:
                    batches.append({"points_by_cohort": values})
            days[observed] = {"date": observed, "available_places": places, "deployment_batches": batches}
        return [days[key] for key in sorted(days)], invalid

    @classmethod
    def missing(cls, counts: dict[str, int], capacity_days: int, unknown_domains: list[int], unknown_sizes: list[int],
                unknown_cohorts: list[int], invalid_capacity: bool) -> list[str]:
        missing = []
        if unknown_domains:
            missing.append("planned domain")
        if unknown_sizes:
            missing.append("story points")
        if unknown_cohorts:
            missing.append("comparable cohort")
        if not counts or any(count < MIN_DELIVERED_OUTCOMES for count in counts.values()):
            missing.append("comparable delivery history")
        if capacity_days < MIN_CAPACITY_DAYS or invalid_capacity:
            missing.append("observed capacity")
        return missing

    @classmethod
    def calendar_missing(cls, calendar: dict, as_of: date | None) -> list[str]:
        if as_of is None:
            return ["forecast date"]
        current_end = cls.day(calendar.get("current_end"))
        next_end = cls.day(calendar.get("next_end"))
        supplied_end = calendar.get("current_end") not in (None, "")
        supplied_next = calendar.get("next_end") not in (None, "")
        if supplied_end and current_end is None or supplied_next and next_end is None:
            return ["sprint calendar"]
        return ["sprint calendar"] if invalid_dates(current_end, next_end) else []

    @classmethod
    def prepared(cls, tasks: list[dict], counts: dict[str, int], blocks: list[dict], missing: list[str],
                 unknown_domains: list[int], unknown_sizes: list[int], unknown_cohorts: list[int],
                 unknown_scope: list[int], invalid_capacity: bool, source: dict, calendar: dict, as_of: date | None,
                 input_cut: str, seed: int) -> dict:
        current_end = cls.day(calendar.get("current_end"))
        next_end = cls.day(calendar.get("next_end"))
        return {"status": "not enough history" if missing else "forecast",
                "constraint_status": "unknown constraints" if unknown_cohorts or unknown_scope or invalid_capacity or cls.calendar_missing(calendar, as_of) else "known",
                "as_of": as_of.isoformat() if as_of else None, "input_cut": input_cut,
                "method_version": METHOD_VERSION, "seed": seed,
                "trials": cls.positive(source.get("trials"), DEFAULT_TRIALS),
                "horizon_sprints": cls.positive(source.get("horizon_sprints"), DEFAULT_HORIZON_SPRINTS),
                "current_end": current_end.isoformat() if current_end else None,
                "next_end": next_end.isoformat() if next_end else None,
                "next_status": "scheduled" if next_end else "next cycle not scheduled",
                "past_deadline": bool(current_end and as_of and as_of >= current_end),
                "delivered_outcomes": sum(counts.values()), "minimum_comparable_outcomes": MIN_DELIVERED_OUTCOMES,
                "observed_capacity_days": len(blocks), "minimum_capacity_days": MIN_CAPACITY_DAYS,
                "cohort_support": [{"cohort": json.loads(key), "delivered_outcomes": count,
                                    "minimum_comparable_outcomes": MIN_DELIVERED_OUTCOMES} for key, count in sorted(counts.items())],
                "capacity": cls.capacity_summary(blocks) if blocks else None,
                "scope": cls.scope_summary(tasks, source.get("scope", ())),
                "unknown_sizes": unknown_sizes, "unknown_domains": unknown_domains,
                "unknown_constraints": sorted(set(unknown_cohorts) | set(unknown_scope)), "cohort_domain": cls.only_domain(tasks),
                "cohort_size_unit": "story points", "pooled_domains": [], "missing_evidence": missing,
                "execution_merges": source.get("execution_merges")}

    @classmethod
    def abstention(cls, prepared: dict) -> dict:
        history_missing = {"comparable delivery history", "observed capacity"} & set(prepared["missing_evidence"])
        status = "unknown constraints" if prepared["constraint_status"] == "unknown constraints" and not history_missing else "not enough history"
        return {**prepared, "status": status, "probability_this_sprint": None, "probability_next_sprint": None,
                "probability_later": None, "this_sprint": None, "next_sprint": None, "later": None,
                "carry_over": None, "bands": None, "p50": None, "p85": None,
                "probability_beyond_horizon": None, "conditional_scenarios": [], "plan_forecasts": [],
                "sensitivity": {"status": "abstained", "reason": "the required history or shared capacity is missing"}}

    @staticmethod
    def capacity_summary(blocks: list[dict]) -> dict:
        places = [row["available_places"] for row in blocks]
        return {"status": "observed", "daily_observations": len(blocks),
                "zero_capacity_days": sum(value == 0 for value in places),
                "zero_output_days": sum(not row["deployment_batches"] for row in blocks),
                "available_places": {"minimum": min(places), "maximum": max(places)}}

    @classmethod
    def scope_summary(cls, tasks: list[dict], source_scope=()) -> dict:
        rows = [row for row in source_scope if isinstance(row, dict) and row.get("delivery_status") not in ("delivered", "removed")]
        if not rows:
            rows = tasks
        known_sizes = {row["task_id"]: row["size_points"] for row in rows
                       if isinstance(row.get("task_id"), int) and isinstance(row.get("size_points"), int)
                       and not isinstance(row.get("size_points"), bool) and row["size_points"] > 0}
        task_ids = sorted({row["task_id"] for row in rows if isinstance(row.get("task_id"), int)})
        unknown_sizes = sorted(task_id for task_id in task_ids if task_id not in known_sizes)
        known_points = sum(known_sizes.values())
        plan_ids = sorted({row["plan_id"] for row in rows if isinstance(row.get("plan_id"), int)})
        unknown_constraint_ids = {row.get("task_id") for row in rows
                                  if not all(cls.cohort(row.get("cohort") or {}).values()) or row.get("approved_scope") is False}
        cohorts = {}
        for row in tasks:
            key = row["cohort_key"]
            value = cohorts.setdefault(key, {"cohort": json.loads(key), "plan_ids": [], "task_ids": [], "remaining_size_points": 0})
            value["plan_ids"].append(row["plan_id"])
            value["task_ids"].append(row["task_id"])
            value["remaining_size_points"] += row["size_points"]
        grouped = [{**value, "plan_ids": sorted(set(value["plan_ids"])), "task_ids": sorted(set(value["task_ids"]))}
                   for _key, value in sorted(cohorts.items())]
        return {"task_ids": task_ids or sorted(row["task_id"] for row in tasks),
                "plan_ids": plan_ids or sorted({row["plan_id"] for row in tasks}),
                "remaining_size_points": None if unknown_sizes else known_points,
                "known_remaining_size_points": known_points, "unknown_size_tasks": len(unknown_sizes),
                "unknown_domain_tasks": sum(not (row.get("cohort") or {}).get("domain") for row in rows),
                "unknown_constraint_tasks": len(unknown_constraint_ids),
                "tasks": [{"task_id": row.get("task_id"), "plan_id": row.get("plan_id"),
                           "size_points": known_sizes.get(row.get("task_id")), "cohort": row.get("cohort") or {},
                           "delivery_status": row.get("delivery_status", "unknown"),
                           "approved_scope": row.get("approved_scope", True)} for row in rows],
                "by_cohort": grouped}

    @staticmethod
    def only_domain(tasks: list[dict]) -> str | None:
        domains = {row["cohort"]["domain"] for row in tasks}
        return next(iter(domains)) if len(domains) == 1 else None

    @staticmethod
    def positive(value, fallback: int) -> int:
        return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else fallback

    @staticmethod
    def day(value: object) -> date | None:
        if not isinstance(value, str):
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    @classmethod
    def simulations(cls, tasks: list[dict], blocks: list[dict], as_of: date | None, horizon_days: int,
                    trials: int, seed: int, calendar: dict) -> tuple[dict, list[dict]]:
        replicates = min(100, trials)
        per_replicate, remainder = divmod(trials, replicates)
        simulated = {"sprint": [], "plans": {plan_id: [] for plan_id in sorted({row["plan_id"] for row in tasks})}}
        batches = []
        for replicate in range(replicates):
            pool_random = random.Random(seed + replicate * 2 + 1)
            pool = [pool_random.choice(blocks) for _ in blocks]
            count = per_replicate + int(replicate < remainder)
            trial_random = random.Random(seed + replicate * 2 + 2)
            batch = {"sprint": [], "plans": {plan_id: [] for plan_id in simulated["plans"]}}
            for _trial in range(count):
                sprint_finish, plan_finish = cls.simulate(tasks, pool, as_of, horizon_days, trial_random)
                batch["sprint"].append(sprint_finish)
                simulated["sprint"].append(sprint_finish)
                for plan_id, dates in simulated["plans"].items():
                    finish = plan_finish.get(plan_id)
                    batch["plans"][plan_id].append(finish)
                    dates.append(finish)
            batches.append(batch)
        return simulated, batches

    @classmethod
    def simulate(cls, tasks: list[dict], blocks: list[dict], as_of: date | None,
                 horizon_days: int, rng: random.Random) -> tuple[date | None, dict[int, date | None]]:
        progress = {row["task_id"]: 0 for row in tasks}
        task_finishes = {}
        plan_ids = sorted({row["plan_id"] for row in tasks})
        plan_finishes = {plan_id: None for plan_id in plan_ids}
        if not tasks:
            return as_of, {plan_id: as_of for plan_id in plan_ids}
        for offset in range(1, horizon_days + 1):
            day = rng.choice(blocks)
            if day["available_places"] == 0:
                continue
            for batch in day["deployment_batches"]:
                cls.allocate(tasks, batch["points_by_cohort"], progress, task_finishes, as_of, offset)
                cls.mark_plans(tasks, task_finishes, plan_finishes)
                if len(task_finishes) == len(tasks):
                    return cls.finish_date(as_of, offset), plan_finishes
        return None, plan_finishes

    @classmethod
    def allocate(cls, tasks: list[dict], output: dict[str, int], progress: dict[int, int],
                 task_finishes: dict[int, date | None], as_of: date | None, offset: int) -> None:
        for cohort_key, points in output.items():
            remaining = points
            ordered = sorted((row for row in tasks if row["cohort_key"] == cohort_key and row["task_id"] not in task_finishes),
                             key=cls.task_order)
            for task in ordered:
                used = min(remaining, task["size_points"] - progress[task["task_id"]])
                progress[task["task_id"]] += used
                remaining -= used
                if progress[task["task_id"]] >= task["size_points"]:
                    task_finishes[task["task_id"]] = cls.finish_date(as_of, offset)
                if remaining <= 0:
                    break

    @staticmethod
    def task_order(task: dict) -> tuple:
        waiting = task.get("delivery_status") in ("awaiting_deployment", "awaiting_evidence")
        return (0 if waiting else 1, task["plan_id"], task["task_id"])

    @staticmethod
    def mark_plans(tasks: list[dict], task_finishes: dict[int, date | None],
                   plan_finishes: dict[int, date | None]) -> None:
        for plan_id in plan_finishes:
            ids = [row["task_id"] for row in tasks if row["plan_id"] == plan_id]
            if ids and all(task_id in task_finishes for task_id in ids) and plan_finishes[plan_id] is None:
                plan_finishes[plan_id] = max(task_finishes[task_id] for task_id in ids)

    @staticmethod
    def finish_date(as_of: date | None, offset: int) -> date | None:
        return as_of + timedelta(days=offset) if as_of else None

    @classmethod
    def distribution(cls, simulations: dict, prepared: dict, capacity_days: int) -> dict:
        calendar = {"current_end": cls.day(prepared.get("current_end")), "next_end": cls.day(prepared.get("next_end"))}
        dates = simulations["sprint"]
        bands, counts = cls.bands(dates, calendar)
        return {**prepared, "status": "forecast", "bands": bands,
                "probability_this_sprint": bands["this_sprint"], "probability_next_sprint": bands["next_sprint"],
                "probability_later": bands["later"], "this_sprint": bands["this_sprint"],
                "next_sprint": bands["next_sprint"], "later": bands["later"],
                "carry_over": cls.carry_over(bands), "p50": cls.quantile(dates, 0.50), "p85": cls.quantile(dates, 0.85),
                "probability_beyond_horizon": cls.percent(counts["beyond"], len(dates)),
                "conditional_scenarios": [], "capacity_days_used": capacity_days}

    @classmethod
    def plan_distributions(cls, simulations: dict, prepared: dict) -> list[dict]:
        calendar = {"current_end": cls.day(prepared.get("current_end")), "next_end": cls.day(prepared.get("next_end"))}
        rows = []
        for plan_id, dates in sorted(simulations["plans"].items()):
            bands, counts = cls.bands(dates, calendar)
            rows.append({"plan_id": plan_id, "p50": cls.quantile(dates, 0.50), "p85": cls.quantile(dates, 0.85),
                         "bands": bands, "probability_this_sprint": bands["this_sprint"],
                         "probability_next_sprint": bands["next_sprint"], "probability_later": bands["later"],
                         "carry_over": cls.carry_over(bands),
                         "probability_beyond_horizon": cls.percent(counts["beyond"], len(dates))})
        return rows

    @classmethod
    def bands(cls, dates: list[date | None], calendar: dict) -> tuple[dict, dict]:
        current_end, next_end = calendar["current_end"], calendar["next_end"]
        if current_end is None:
            return {"this_sprint": None, "next_sprint": None, "later": None}, {"beyond": dates.count(None)}
        this_count = sum(value is not None and value < current_end for value in dates)
        beyond = dates.count(None)
        if next_end is None:
            this = cls.percent(this_count, len(dates))
            return {"this_sprint": this, "next_sprint": None, "later": None}, {"beyond": beyond}
        next_count = sum(value is not None and current_end <= value < next_end for value in dates)
        later_count = len(dates) - this_count - next_count
        bands = cls.rounded_bands(this_count, next_count, later_count, len(dates))
        return bands, {"beyond": beyond}

    @classmethod
    def rounded_bands(cls, this: int, next_: int, later: int, total: int) -> dict:
        counts = {"this_sprint": this, "next_sprint": next_, "later": later}
        raw = {key: value * 100 / total for key, value in counts.items()}
        rounded = {key: math.floor(value) for key, value in raw.items()}
        left = 100 - sum(rounded.values())
        for key in sorted(raw, key=lambda name: (-(raw[name] - rounded[name]), name))[:left]:
            rounded[key] += 1
        return rounded

    @classmethod
    def sensitivity(cls, batches: list[dict], prepared: dict) -> dict:
        calendar = {"current_end": cls.day(prepared.get("current_end")), "next_end": cls.day(prepared.get("next_end"))}
        samples = {name: [] for name in ("this_sprint", "next_sprint", "later")}
        for batch in batches:
            bands, _counts = cls.bands(batch["sprint"], calendar)
            for name in samples:
                if bands[name] is not None:
                    samples[name].append(bands[name])
        return {"status": "observed block bootstrap",
                "label": "Conditional range over resampled observed days; not a calibration guarantee.",
                "bands": {name: {"p10": cls.percentile(values, 0.10), "p90": cls.percentile(values, 0.90)}
                          for name, values in samples.items() if values}}

    @classmethod
    def quantile(cls, values: list[date | None], probability: float) -> str | None:
        ordered = sorted(value for value in values if value is not None)
        index = math.ceil(probability * len(values)) - 1
        return ordered[index].isoformat() if 0 <= index < len(ordered) else None

    @staticmethod
    def carry_over(bands: dict) -> int | None:
        if bands["this_sprint"] is None:
            return None
        return 100 - bands["this_sprint"] if bands["next_sprint"] is None else bands["next_sprint"] + bands["later"]

    @staticmethod
    def percent(count: int, total: int) -> int:
        return round(count * 100 / total) if total else 0

    @staticmethod
    def percentile(values: list[int], probability: float) -> int | None:
        if not values:
            return None
        ordered = sorted(values)
        return ordered[round((len(ordered) - 1) * probability)]


def invalid_dates(current_end: date | None, next_end: date | None) -> bool:
    return next_end is not None and (current_end is None or next_end <= current_end)
