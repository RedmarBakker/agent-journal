from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math
import random
from statistics import NormalDist

from journal.features.estimates.support.baseline_forecast import DEFAULT_TRIALS, BaselineForecast
from journal.features.estimates.support.learned_duration_ranges import P85_NORMAL_QUANTILE
from journal.features.tasks.support.ready_order import ReadyOrder


METHOD_VERSION = "shared-network-stage-simulation-v1"


class NetworkForecast:
    """Simulates a shared dependency network from learned task stages and observed capacity."""

    def estimate(self, source: dict, baseline: dict) -> dict:
        tasks = self.tasks(source.get("scope", ()))
        trials = BaselineForecast.positive(source.get("trials"), DEFAULT_TRIALS)
        horizon = self.horizon(source)
        as_of = BaselineForecast.day(source.get("as_of"))
        blocks, invalid_capacity = BaselineForecast.capacity_days(source.get("capacity_days", ()), as_of)
        graph = self.graph(source.get("graph", {}), {row["task_id"] for row in tasks})
        prepared = self.prepared(source, baseline, tasks, trials, horizon, as_of, blocks, graph)
        if not tasks:
            return {**self.public(prepared), "status": "empty", "p50": as_of.isoformat() if as_of else None,
                    "p85": as_of.isoformat() if as_of else None, "task_forecasts": [],
                    "plan_forecasts": [], "domain_forecasts": [],
                    "comparison": self.comparison(as_of.isoformat() if as_of else None,
                                                  as_of.isoformat() if as_of else None,
                                                  prepared["_baseline"])}
        if blocks and not any(row["available_places"] for row in blocks):
            return self.unavailable(prepared, "zero capacity", ["all observed capacity days have zero places"], 100)
        missing = self.missing(tasks, as_of, blocks, horizon, invalid_capacity)
        if missing:
            status = "unknown constraints" if graph["external_conditions"] else "not enough history"
            return self.unavailable(prepared, status, missing)
        runs = self.simulations(tasks, graph, blocks, prepared)
        return self.distributions(runs, tasks, graph, prepared)

    @staticmethod
    def tasks(rows) -> list[dict]:
        grouped = {}
        for raw in rows:
            if not isinstance(raw, dict) or not isinstance(raw.get("task_id"), int):
                continue
            task_id = raw["task_id"]
            plans = raw.get("plan_ids") or ([raw["plan_id"]] if isinstance(raw.get("plan_id"), int) else [])
            if task_id in grouped:
                grouped[task_id]["plan_ids"] = sorted(set(grouped[task_id]["plan_ids"]) | set(plans))
            else:
                grouped[task_id] = {**raw, "plan_ids": sorted(set(plans))}
        return [grouped[key] for key in sorted(grouped)]

    @staticmethod
    def graph(value: dict, task_ids: set[int]) -> dict:
        edges, external, seen = [], [], set()
        conditions = {(row.get("task_id"), row.get("prerequisite_id"), row.get("kind")): row
                      for row in value.get("external_conditions", ()) if isinstance(row, dict)}
        for row in value.get("edges", ()):
            if not isinstance(row, dict) or row.get("task_id") not in task_ids:
                continue
            key = (row.get("task_id"), row.get("prerequisite_id"), row.get("kind"))
            condition = conditions.get(key, {})
            status = condition.get("status", "unresolved")
            prerequisite_id = row.get("prerequisite_id")
            if prerequisite_id in task_ids:
                if status == "resolved":
                    continue
                edge = {**row, "external": False}
            elif status == "resolved":
                continue
            else:
                edge = {**row, "external": True}
                external.append({**edge, "status": "unresolved"})
            if key not in seen:
                seen.add(key)
                edges.append(edge)
        return {"edges": sorted(edges, key=NetworkForecast.edge_key),
                "external_conditions": sorted(external, key=NetworkForecast.edge_key)}

    @staticmethod
    def edge_key(row: dict) -> tuple:
        return row.get("task_id", 0), row.get("prerequisite_id", 0), row.get("kind", "")

    def prepared(self, source: dict, baseline: dict, tasks: list[dict], trials: int, horizon: int,
                 as_of: date | None, blocks: list[dict], graph: dict) -> dict:
        seed = self.seed(source, baseline)
        plans = sorted({plan_id for row in tasks for plan_id in row["plan_ids"]})
        domains = sorted({row.get("domain") for row in tasks if row.get("domain")})
        input_cut = self.fingerprint({"source": source, "baseline": self.baseline_summary(baseline)})
        return {"method_version": METHOD_VERSION, "input_cut": input_cut, "seed": seed,
                "trials": trials, "horizon_days": horizon, "horizon_end":
                (as_of + timedelta(days=horizon)).isoformat() if as_of else None,
                "as_of": as_of.isoformat() if as_of else None, "plan_ids": plans, "domains": domains,
                "external_conditions": graph["external_conditions"], "capacity_days_used": len(blocks),
                "wip_limits": source.get("wip_limits", {}), "mode": source.get("mode", "report"),
                "calendar": source.get("calendar", {}), "_ready_forecasts": source.get("ready_forecasts", {}),
                "sprint_miss_warning_percent": source.get("sprint_miss_warning_percent", 70),
                "stage_wait_accounting": "learned elapsed durations include waits; shared places admit starts and batches admit delivery without adding a second per-task queue delay",
                "_scope": tasks, "_baseline": self.baseline_summary(baseline)}

    @staticmethod
    def missing(tasks: list[dict], as_of: date | None, blocks: list[dict], horizon: int,
                invalid_capacity: bool) -> list[str]:
        missing = []
        if as_of is None:
            missing.append("forecast date")
        if not blocks:
            missing.append("observed shared capacity")
        if invalid_capacity:
            missing.append("valid shared capacity records")
        if horizon < 1:
            missing.append("bounded simulation horizon")
        for task in tasks:
            task_id = task["task_id"]
            if not isinstance(task.get("size_points"), int) or isinstance(task.get("size_points"), bool) or task["size_points"] < 1:
                missing.append(f"task {task_id} story points")
            if not task.get("domain") or not task.get("cohort_key"):
                missing.append(f"task {task_id} cohort")
            if not NetworkForecast.has_delivery_capacity(task, blocks):
                missing.append(f"task {task_id} shared delivery capacity")
            stage_names = ("delivery_delay",) if task.get("current_stage") == "delivery_delay" else ("execution_cycle", "delivery_delay")
            for stage_name in stage_names:
                stage = task.get("stages", {}).get(stage_name, {})
                if not NetworkForecast.valid_duration(stage):
                    missing.append(f"task {task_id} {stage_name} duration")
        return sorted(set(missing))

    @staticmethod
    def has_delivery_capacity(task: dict, blocks: list[dict]) -> bool:
        cohort, size = task.get("cohort_key"), task.get("size_points")
        if not isinstance(size, int) or isinstance(size, bool) or size < 1:
            return False
        return any(isinstance(batch, dict)
                   and isinstance(batch.get("points_by_cohort"), dict)
                   and batch["points_by_cohort"].get(cohort, 0) >= size
                   for block in blocks for batch in block["deployment_batches"])

    @staticmethod
    def valid_duration(stage: dict) -> bool:
        p50, p85 = stage.get("p50_seconds"), stage.get("p85_seconds")
        return (stage.get("status") == "forecast" and isinstance(p50, (int, float)) and not isinstance(p50, bool)
                and isinstance(p85, (int, float)) and not isinstance(p85, bool) and p50 >= 0 and p85 >= p50
                and (p50 > 0 or p85 == 0))

    def unavailable(self, prepared: dict, status: str, missing: list[str], beyond: int = 0) -> dict:
        result = {**prepared, "status": status, "missing_evidence": missing, "p50": None, "p85": None,
                  "probability_this_sprint": None, "probability_next_sprint": None, "probability_later": None,
                  "bands": {"this_sprint": None, "next_sprint": None, "later": None},
                  "probability_beyond_horizon": beyond, "plan_forecasts": [],
                  "domain_forecasts": [], "diagnostics": {"maximum_execution_wip": 0,
                                                              "maximum_worker_queue_wip": 0,
                                                              "maximum_plan_delivery_wip": 0,
                                                              "maximum_domain_delivery_wip": 0,
                                                              "deployment_batches_used": 0},
                  "task_forecasts": [{"task_id": row["task_id"], "status": status, "p50": None, "p85": None}
                                     for row in prepared["_scope"]]}
        probability_error = 0 if status == "zero capacity" else None
        return {**self.public(result),
                "uncertainty": {"monte_carlo": self.empty_error(prepared["trials"], probability_error),
                                "history": self.history_uncertainty(prepared["_scope"])},
                "comparison": self.comparison(None, None, prepared["_baseline"])}

    def simulations(self, tasks: list[dict], graph: dict, blocks: list[dict], prepared: dict) -> list[dict]:
        seed = prepared["seed"]
        runs = []
        for trial in range(prepared["trials"]):
            rng = random.Random(seed + trial * 7919)
            durations = self.sample_stages(tasks, rng)
            run = self.simulate(tasks, graph, blocks, prepared, durations, random.Random(seed + trial * 104729 + 1))
            runs.append(run)
        return runs

    def sample_stages(self, tasks: list[dict], rng: random.Random) -> dict[int, dict]:
        shared = {}
        sampled = {}
        for task in tasks:
            cohort = tuple(sorted(task.get("stage_cohort", {}).items())) or task["cohort_key"]
            stage_values = {}
            for stage_name in ("execution_cycle", "delivery_delay"):
                if stage_name == "execution_cycle" and task.get("current_stage") == "delivery_delay":
                    stage_values[stage_name] = 0.0
                    continue
                stage = task["stages"][stage_name]
                key = cohort, stage_name
                if key not in shared:
                    shared[key] = rng.random()
                age = task.get("age_seconds", 0) if task.get("current_stage") == stage_name else 0
                stage_values[stage_name] = self.duration_remaining(stage, age, shared[key]) / 86400
            sampled[task["task_id"]] = stage_values
        return sampled

    @staticmethod
    def duration_remaining(stage: dict, age_seconds: float, uniform: float) -> float:
        p50, p85 = stage["p50_seconds"], stage["p85_seconds"]
        if p50 == p85:
            return max(0.0, p50 - age_seconds)
        sigma = math.log(p85 / p50) / P85_NORMAL_QUANTILE
        age = max(0.0, age_seconds)
        lower = NormalDist().cdf(math.log(age / p50) / sigma) if age else 0.0
        quantile = min(1 - 1e-12, max(1e-12, lower + uniform * (1 - lower)))
        total = p50 * math.exp(sigma * NormalDist().inv_cdf(quantile))
        return max(0.0, total - age)

    def simulate(self, tasks: list[dict], graph: dict, blocks: list[dict], prepared: dict,
                 durations: dict[int, dict], rng: random.Random) -> dict:
        states = self.initial_states(tasks, durations)
        worker_count = max(row["available_places"] for row in blocks)
        queues = [[] for _ in range(worker_count)]
        self.queue_started(tasks, states, queues, prepared)
        incoming = self.incoming(graph)
        resource_edges: list[tuple[int, int, str]] = []
        last_finished = [None] * worker_count
        batch_count = 0
        max_execution = sum(row["started"] and row["execution_finish"] is None for row in states.values())
        max_worker_queue = max(map(len, queues), default=0)
        max_plan_delivery = self.maximum_plan_delivery(tasks, states)
        max_domain_delivery = self.maximum_domain_delivery(tasks, states)
        for offset in range(1, prepared["horizon_days"] + 1):
            current = offset - 1
            block = rng.choice(blocks)
            batch_count += self.deliver(block, tasks, states, current, prepared, resource_edges)
            self.assign(tasks, states, queues, incoming, prepared, current)
            max_worker_queue = max(max_worker_queue, max(map(len, queues), default=0))
            places = min(block["available_places"], worker_count)
            self.start_queued(tasks, states, queues, incoming, prepared, current, places, resource_edges, last_finished)
            max_execution = max(max_execution, self.execution_count(states))
            self.work(queues, states, offset, last_finished)
            max_execution = max(max_execution, self.execution_count(states))
            max_worker_queue = max(max_worker_queue, max(map(len, queues), default=0))
            max_plan_delivery = max(max_plan_delivery, self.maximum_plan_delivery(tasks, states))
            max_domain_delivery = max(max_domain_delivery, self.maximum_domain_delivery(tasks, states))
        finishes = {task_id: state["delivery_date"] for task_id, state in states.items()}
        plan_ids = sorted({plan_id for row in tasks for plan_id in row["plan_ids"]})
        domains = sorted({row.get("domain") for row in tasks if row.get("domain")})
        plans = {plan_id: self.group_finish(tasks, finishes, "plan_ids", plan_id, prepared["as_of"]) for plan_id in plan_ids}
        domain_finishes = {domain: self.group_finish(tasks, finishes, "domain", domain, prepared["as_of"]) for domain in domains}
        critical = self.critical_sets(tasks, graph, states, resource_edges, finishes, plans, domain_finishes)
        return {"finish": self.group_finish(tasks, finishes, None, None, prepared["as_of"]),
                "tasks": finishes, "plans": plans, "domains": domain_finishes, "critical": critical,
                "maximum_execution_wip": max_execution, "maximum_worker_queue_wip": max_worker_queue,
                "maximum_plan_delivery_wip": max_plan_delivery, "maximum_domain_delivery_wip": max_domain_delivery,
                "deployment_batches_used": batch_count}

    @staticmethod
    def initial_states(tasks: list[dict], durations: dict[int, dict]) -> dict[int, dict]:
        states = {}
        for task in tasks:
            task_id = task["task_id"]
            current_delivery = task.get("current_stage") == "delivery_delay"
            states[task_id] = {"started": bool(task.get("started")),
                               "execution_remaining": durations[task_id]["execution_cycle"],
                               "delivery_duration": durations[task_id]["delivery_delay"],
                               "execution_finish": 0.0 if current_delivery else None,
                               "execution_start": 0.0 if task.get("started") and not current_delivery else None,
                               "delivery_due": durations[task_id]["delivery_delay"] if current_delivery else None,
                               "delivery_finish": None, "delivery_date": None}
        return states

    @staticmethod
    def queue_started(tasks: list[dict], states: dict[int, dict], queues: list[list[int]], prepared: dict) -> None:
        started = [row for row in tasks if states[row["task_id"]]["started"]
                   and states[row["task_id"]]["execution_finish"] is None]
        for task in sorted(started, key=lambda row: NetworkForecast.ready_key(row, prepared, 0)):
            if queues:
                seat = min(range(len(queues)), key=lambda index: (len(queues[index]), index))
                queues[seat].append(task["task_id"])

    def assign(self, tasks: list[dict], states: dict[int, dict], queues: list[list[int]], incoming: dict,
               prepared: dict, current: int) -> None:
        queued = {task_id for queue in queues for task_id in queue}
        available = [row for row in tasks if not states[row["task_id"]]["started"]
                     and states[row["task_id"]]["execution_finish"] is None
                     and row["task_id"] not in queued and self.ready(row["task_id"], incoming, states)]
        for row in sorted(available, key=lambda task: self.ready_key(task, prepared, current)):
            seat = self.queue_seat(queues, prepared["wip_limits"].get("worker_queue", 0))
            if seat is None:
                break
            queues[seat].append(row["task_id"])

    @staticmethod
    def queue_seat(queues: list[list[int]], limit: int) -> int | None:
        if not queues:
            return None
        available = [index for index, queue in enumerate(queues) if limit == 0 or len(queue) < limit]
        return min(available, key=lambda index: (len(queues[index]), index)) if available else None

    def start_queued(self, tasks: list[dict], states: dict[int, dict], queues: list[list[int]], incoming: dict,
                     prepared: dict, current: int, places: int, resource_edges: list[tuple[int, int, str]],
                     last_finished: list[int | None]) -> None:
        for seat, queue in enumerate(queues):
            if self.execution_count(states) >= places:
                break
            if not queue:
                continue
            task_id = queue[0]
            state = states[task_id]
            if state["started"] or not self.ready(task_id, incoming, states):
                continue
            if not self.can_start(tasks, states, task_id, prepared["wip_limits"]):
                continue
            state["started"] = True
            state["execution_start"] = current
            previous = last_finished[seat]
            if previous is not None and states[previous]["execution_finish"] <= current:
                resource_edges.append((task_id, previous, "resource"))

    @staticmethod
    def can_start(tasks: list[dict], states: dict[int, dict], task_id: int, limits: dict) -> bool:
        execution_limit = limits.get("execution", 0)
        if execution_limit and NetworkForecast.execution_count(states) >= execution_limit:
            return False
        candidate = next(row for row in tasks if row["task_id"] == task_id)
        pending = [row for row in tasks if states[row["task_id"]]["started"] and states[row["task_id"]]["delivery_finish"] is None]
        plan_limit = limits.get("plan_delivery", 0)
        if plan_limit and any(sum(plan_id in row["plan_ids"] for row in pending) >= plan_limit
                              for plan_id in candidate["plan_ids"]):
            return False
        domain_limit = limits.get("domain_delivery", 0)
        if domain_limit and sum(row.get("domain") == candidate.get("domain") for row in pending) >= domain_limit:
            return False
        return True

    @staticmethod
    def execution_count(states: dict[int, dict]) -> int:
        return sum(state["started"] and state["execution_finish"] is None for state in states.values())

    def work(self, queues: list[list[int]], states: dict[int, dict], offset: int,
             last_finished: list[int | None]) -> None:
        for seat, queue in enumerate(queues):
            if not queue:
                continue
            task_id = queue[0]
            state = states[task_id]
            if not state["started"] or state["execution_finish"] is not None:
                continue
            if state["execution_remaining"] <= 0:
                finish = offset - 1
            else:
                state["execution_remaining"] -= 1
                finish = offset if state["execution_remaining"] <= 0 else None
            if finish is None:
                continue
            state["execution_finish"] = finish
            state["delivery_due"] = finish + state["delivery_duration"]
            queue.pop(0)
            last_finished[seat] = task_id

    @staticmethod
    def maximum_plan_delivery(tasks: list[dict], states: dict[int, dict]) -> int:
        plans = {plan_id for row in tasks for plan_id in row["plan_ids"]}
        return max((sum(plan_id in row["plan_ids"] and states[row["task_id"]]["started"]
                        and states[row["task_id"]]["delivery_finish"] is None for row in tasks)
                    for plan_id in plans), default=0)

    @staticmethod
    def maximum_domain_delivery(tasks: list[dict], states: dict[int, dict]) -> int:
        domains = {row.get("domain") for row in tasks}
        return max((sum(row.get("domain") == domain and states[row["task_id"]]["started"]
                        and states[row["task_id"]]["delivery_finish"] is None for row in tasks)
                    for domain in domains), default=0)

    def deliver(self, block: dict, tasks: list[dict], states: dict[int, dict], current: int,
                prepared: dict, resource_edges: list[tuple[int, int, str]]) -> int:
        used = 0
        if block["available_places"] == 0:
            return used
        for batch in block["deployment_batches"]:
            capacity = batch.get("points_by_cohort", {}) if isinstance(batch, dict) else {}
            accepted = False
            cohorts = set(capacity)
            for cohort in sorted(cohorts):
                points = capacity.get(cohort, 0)
                if not isinstance(points, int) or isinstance(points, bool) or points < 1:
                    continue
                last_accepted = None
                candidates = [row for row in tasks if row.get("cohort_key") == cohort
                              and states[row["task_id"]]["delivery_date"] is None
                              and states[row["task_id"]]["delivery_due"] is not None
                              and states[row["task_id"]]["delivery_due"] <= current]
                for row in sorted(candidates, key=lambda task: self.ready_key(task, prepared, current)):
                    size = row["size_points"]
                    if size > points:
                        if last_accepted is not None:
                            resource_edges.append((row["task_id"], last_accepted, "delivery_resource"))
                        continue
                    points -= size
                    state = states[row["task_id"]]
                    state["delivery_finish"] = current
                    state["delivery_date"] = (date.fromisoformat(prepared["as_of"]) + timedelta(days=current)).isoformat()
                    accepted = True
                    last_accepted = row["task_id"]
            used += int(accepted)
        return used

    @staticmethod
    def incoming(graph: dict) -> dict[int, list[dict]]:
        incoming = {}
        for edge in graph["edges"]:
            incoming.setdefault(edge["task_id"], []).append(edge)
        return incoming

    @staticmethod
    def ready(task_id: int, incoming: dict[int, list[dict]], states: dict[int, dict]) -> bool:
        for edge in incoming.get(task_id, ()):
            if edge.get("external"):
                return False
            prerequisite = states.get(edge["prerequisite_id"])
            if prerequisite is None:
                return False
            barrier = prerequisite["execution_finish"] if edge["kind"] == "prerequisite" else prerequisite["delivery_finish"]
            if barrier is None:
                return False
        return True

    @staticmethod
    def ready_key(task: dict, prepared: dict, current: int) -> tuple:
        if prepared["mode"] == "off":
            return -task.get("priority", 0), task["task_id"]
        forecasts = prepared["_ready_forecasts"]
        candidates = []
        for plan_id in task["plan_ids"]:
            value = forecasts.get(str(plan_id), forecasts.get(plan_id, {})) or {}
            sprint = value.get("sprint") or {}
            candidates.append((sprint.get("ends_on", "9999-12-31"), plan_id, value))
        forecast = min(candidates, default=("9999-12-31", 0, {}))[2]
        now = datetime.combine(date.fromisoformat(prepared["as_of"]) + timedelta(days=current), datetime.min.time(), timezone.utc)
        return ReadyOrder.rank_key(task, forecast, now, prepared["sprint_miss_warning_percent"])

    @staticmethod
    def group_finish(tasks: list[dict], finishes: dict[int, str | None], member: str | None,
                     value, as_of: str | None) -> str | None:
        rows = [row for row in tasks if member is None or (value in row.get(member, []) if member == "plan_ids" else row.get(member) == value)]
        dates = [finishes[row["task_id"]] for row in rows]
        if not rows or any(day is None for day in dates):
            return None
        return max(dates)

    def critical_sets(self, tasks: list[dict], graph: dict, states: dict[int, dict],
                      resource_edges: list[tuple[int, int, str]], finishes: dict[int, str | None],
                      plans: dict[int, str | None], domains: dict[str, str | None]) -> dict:
        dependencies = [(edge["task_id"], edge["prerequisite_id"], edge["kind"])
                        for edge in graph["edges"] if not edge.get("external")]
        dependencies.extend(resource_edges)
        dependencies = sorted(set(dependencies))
        by_plan, by_domain = {}, {}
        for plan_id, finish in plans.items():
            ids = {row["task_id"] for row in tasks if plan_id in row["plan_ids"]}
            terminals = {task_id for task_id in ids if finishes[task_id] == finish and finish is not None}
            by_plan[plan_id] = self.ancestors(terminals, dependencies, states)
        for domain, finish in domains.items():
            ids = {row["task_id"] for row in tasks if row.get("domain") == domain}
            terminals = {task_id for task_id in ids if finishes[task_id] == finish and finish is not None}
            by_domain[domain] = self.ancestors(terminals, dependencies, states)
        all_finish = self.group_finish(tasks, finishes, None, None, None)
        terminals = {task_id for task_id, finish in finishes.items() if finish == all_finish and finish is not None}
        return {"plans": by_plan, "domains": by_domain,
                "all": self.ancestors(terminals, dependencies, states)}

    @staticmethod
    def ancestors(terminals: set[int], edges: list[tuple[int, int, str]], states: dict[int, dict]) -> set[int]:
        critical = set(terminals)
        pending = list(terminals)
        while pending:
            dependent = pending.pop()
            dependent_state = states[dependent]
            start = dependent_state["execution_start"]
            for target, prerequisite, kind in edges:
                if target != dependent:
                    continue
                prior = states[prerequisite]
                if kind == "delivery_resource":
                    barrier = prior["delivery_finish"]
                    finish = dependent_state["delivery_finish"]
                    critical_edge = barrier is not None and finish is not None and barrier < finish
                else:
                    barrier = prior["execution_finish"] if kind in ("prerequisite", "resource") else prior["delivery_finish"]
                    critical_edge = barrier is not None and start is not None and (
                        barrier <= start if kind == "resource" else abs(barrier - start) < 1e-9)
                if critical_edge and prerequisite not in critical:
                    critical.add(prerequisite)
                    pending.append(prerequisite)
        return critical

    def distributions(self, runs: list[dict], tasks: list[dict], graph: dict, prepared: dict) -> dict:
        dates = [run["finish"] for run in runs]
        blocked = self.external_blocked_tasks(graph)
        bands, _counts = BaselineForecast.bands([self.day(value) for value in dates], prepared["calendar"])
        plan_forecasts = [self.group_distribution(runs, tasks, "plans", plan_id, prepared, blocked)
                          for plan_id in prepared["plan_ids"]]
        domain_forecasts = [self.group_distribution(runs, tasks, "domains", domain, prepared, blocked)
                            for domain in prepared["domains"]]
        for row in plan_forecasts:
            group_ids = {task["task_id"] for task in tasks if row["plan_id"] in task["plan_ids"]}
            if group_ids & blocked and row["p50"] is None:
                row["status"] = "unknown constraints"
        for row in domain_forecasts:
            group_ids = {task["task_id"] for task in tasks if task.get("domain") == row["domain"]}
            if group_ids & blocked and row["p50"] is None:
                row["status"] = "unknown constraints"
        task_forecasts = [self.task_distribution(runs, row, prepared, blocked) for row in tasks]
        finish_probability = sum(value is not None for value in dates) / len(dates)
        status = "unknown constraints" if graph["external_conditions"] else "forecast" if finish_probability else "beyond horizon"
        p50 = BaselineForecast.quantile([self.day(value) for value in dates], 0.5)
        p85 = BaselineForecast.quantile([self.day(value) for value in dates], 0.85)
        baseline_plans = {row.get("plan_id"): row for row in prepared["_baseline"].get("plan_forecasts", ())}
        for row in plan_forecasts:
            row["comparison"] = self.comparison(row["p50"], row["p85"], baseline_plans.get(row["plan_id"], {}))
        result = {**prepared, "status": status, "p50": p50,
                  "p85": p85,
                  "bands": bands, "probability_this_sprint": bands["this_sprint"],
                  "probability_next_sprint": bands["next_sprint"], "probability_later": bands["later"],
                  "probability_beyond_horizon": BaselineForecast.percent(dates.count(None), len(dates)),
                  "plan_forecasts": plan_forecasts, "domain_forecasts": domain_forecasts,
                  "task_forecasts": task_forecasts,
                  "diagnostics": {"maximum_execution_wip": max(run["maximum_execution_wip"] for run in runs),
                                  "maximum_worker_queue_wip": max(run["maximum_worker_queue_wip"] for run in runs),
                                  "maximum_plan_delivery_wip": max(run["maximum_plan_delivery_wip"] for run in runs),
                                  "maximum_domain_delivery_wip": max(run["maximum_domain_delivery_wip"] for run in runs),
                                  "deployment_batches_used": round(sum(run["deployment_batches_used"] for run in runs) / len(runs), 3)},
                  "uncertainty": {"monte_carlo": self.numerical_error(runs, prepared),
                                  "history": self.history_uncertainty(tasks)},
                  "comparison": self.comparison(p50, p85, prepared["_baseline"])}
        return self.public(result)

    @staticmethod
    def external_blocked_tasks(graph: dict) -> set[int]:
        blocked = {row["task_id"] for row in graph["external_conditions"]}
        while True:
            added = {row["task_id"] for row in graph["edges"]
                     if not row.get("external") and row["prerequisite_id"] in blocked}
            if added <= blocked:
                return blocked
            blocked.update(added)

    def group_distribution(self, runs: list[dict], tasks: list[dict], key: str, value, prepared: dict,
                           blocked: set[int]) -> dict:
        dates = [run[key][value] for run in runs]
        bands, _counts = BaselineForecast.bands([self.day(day) for day in dates], prepared["calendar"])
        group_tasks = [row for row in tasks if (value in row["plan_ids"] if key == "plans" else row.get("domain") == value)]
        critical_count = sum(value is not None for value in dates)
        result = {("plan_id" if key == "plans" else "domain"): value,
                "status": "forecast" if critical_count else "beyond horizon",
                "p50": BaselineForecast.quantile([self.day(day) for day in dates], 0.5),
                "p85": BaselineForecast.quantile([self.day(day) for day in dates], 0.85),
                "bands": bands, "probability_this_sprint": bands["this_sprint"],
                "probability_next_sprint": bands["next_sprint"], "probability_later": bands["later"],
                "probability_beyond_horizon": BaselineForecast.percent(dates.count(None), len(dates)),
                "criticality": self.criticality(runs, key, value, [row["task_id"] for row in group_tasks], len(runs)),
                "task_forecasts": [self.group_task(row, runs, key, value, prepared, blocked) for row in group_tasks]}
        return result

    def group_task(self, task: dict, runs: list[dict], key: str, value, prepared: dict, blocked: set[int]) -> dict:
        forecast = self.task_distribution(runs, task, prepared, blocked)
        critical = sum(task["task_id"] in run["critical"][key][value] for run in runs)
        return {**forecast, "criticality_probability": BaselineForecast.percent(critical, len(runs))}

    def task_distribution(self, runs: list[dict], task: dict, prepared: dict, blocked: set[int] | None = None) -> dict:
        task_id = task["task_id"]
        dates = [run["tasks"][task_id] for run in runs]
        critical = sum(task_id in run["critical"]["all"] for run in runs)
        status = "forecast" if any(dates) else "unknown constraints" if blocked and task_id in blocked else "beyond horizon"
        return {"task_id": task_id, "plan_ids": task["plan_ids"], "domain": task.get("domain"),
                "status": status,
                "p50": BaselineForecast.quantile([self.day(day) for day in dates], 0.5),
                "p85": BaselineForecast.quantile([self.day(day) for day in dates], 0.85),
                "probability_beyond_horizon": BaselineForecast.percent(dates.count(None), len(dates)),
                "criticality_probability": BaselineForecast.percent(critical, len(runs))}

    @staticmethod
    def criticality(runs: list[dict], key: str, value, task_ids: list[int], total: int) -> dict:
        counts = {task_id: sum(task_id in run["critical"][key][value] for run in runs) for task_id in task_ids}
        return {"method": "shared trial dependency and resource paths", "trials": total,
                "critical_task_ids": sorted(task_id for task_id, count in counts.items() if count == total),
                "task_probabilities": {str(task_id): BaselineForecast.percent(count, total) for task_id, count in counts.items()}}

    @staticmethod
    def numerical_error(runs: list[dict], prepared: dict) -> dict:
        bands = [run["finish"] for run in runs]
        end = BaselineForecast.day(prepared["calendar"].get("current_end"))
        probability = sum(BaselineForecast.day(value) is not None and BaselineForecast.day(value) < end for value in bands) / len(runs) if end else None
        return {"trials": len(runs),
                "probability_standard_error_pct": round(math.sqrt(probability * (1 - probability) / len(runs)) * 100, 4) if probability is not None else None,
                "p50_standard_error_days": NetworkForecast.quantile_error(runs, 0.5),
                "p85_standard_error_days": NetworkForecast.quantile_error(runs, 0.85)}

    @staticmethod
    def quantile_error(runs: list[dict], probability: float) -> float | None:
        chunk_count = min(100, len(runs))
        if chunk_count < 2:
            return None
        chunks = [[] for _ in range(chunk_count)]
        for index, row in enumerate(runs):
            chunks[index % chunk_count].append(row["finish"])
        quantiles = [BaselineForecast.day(BaselineForecast.quantile([NetworkForecast.day(value) for value in chunk], probability))
                     for chunk in chunks]
        offsets = [(value - date(1970, 1, 1)).days for value in quantiles if value is not None]
        if len(offsets) < 2:
            return None
        mean = sum(offsets) / len(offsets)
        variance = sum((value - mean) ** 2 for value in offsets) / (len(offsets) - 1)
        return round(math.sqrt(variance / len(offsets)), 4)

    @staticmethod
    def history_uncertainty(tasks: list[dict]) -> dict:
        stages = [stage for row in tasks for stage_name, stage in row.get("stages", {}).items()
                  if (stage_name != "execution_cycle" or row.get("current_stage") != "delivery_delay")]
        samples = [stage.get("completed_samples", 0) for stage in stages]
        limitations = sorted({message for stage in stages for message in stage.get("limitations", ())})
        return {"status": "limited history" if any(value < 10 for value in samples) or limitations else "supported history",
                "task_count": len(tasks), "minimum_completed_samples": min(samples, default=0),
                "minimum_effective_sample_count": min((stage.get("effective_sample_count", 0) for stage in stages), default=0),
                "maximum_censored_samples": max((stage.get("censored_samples", 0) for stage in stages), default=0),
                "limitations": limitations}

    @staticmethod
    def comparison(network_p50: str | None, network_p85: str | None, baseline: dict) -> dict:
        available = baseline.get("status") == "forecast"
        return {"status": "comparable" if available and network_p50 else "baseline or network unavailable",
                "baseline": {"method_version": baseline.get("method_version"), "p50": baseline.get("p50"),
                             "p85": baseline.get("p85")},
                "network": {"p50": network_p50, "p85": network_p85},
                "p50_delta_days": NetworkForecast.date_delta(network_p50, baseline.get("p50")),
                "p85_delta_days": NetworkForecast.date_delta(network_p85, baseline.get("p85")), "selection": "none",
                "interpretation": "Differences expose changed mix, capacity or missing evidence; neither method is selected."}

    @staticmethod
    def date_delta(first: str | None, second: str | None) -> int | None:
        first_day, second_day = BaselineForecast.day(first), BaselineForecast.day(second)
        return (first_day - second_day).days if first_day and second_day else None

    @staticmethod
    def empty_error(trials: int, probability_error: float | None = None) -> dict:
        return {"trials": trials, "probability_standard_error_pct": probability_error,
                "p50_standard_error_days": None, "p85_standard_error_days": None}

    @staticmethod
    def baseline_summary(baseline: dict) -> dict:
        return {key: baseline.get(key) for key in ("status", "method_version", "p50", "p85", "plan_forecasts")}

    @staticmethod
    def public(result: dict) -> dict:
        return {key: value for key, value in result.items() if not key.startswith("_")}

    @staticmethod
    def seed(source: dict, baseline: dict) -> int:
        value = baseline.get("seed", source.get("seed"))
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        return int(NetworkForecast.fingerprint({"source": source, "baseline": NetworkForecast.baseline_summary(baseline)})[:16], 16)

    @staticmethod
    def fingerprint(source: dict) -> str:
        return hashlib.sha256(json.dumps(source, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()

    @classmethod
    def horizon(cls, source: dict) -> int:
        value = source.get("horizon_days")
        if "horizon_days" in source:
            return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            return value
        calendar = source.get("calendar", {})
        sprints = BaselineForecast.positive(source.get("horizon_sprints"), 6)
        sprint_days = BaselineForecast.positive(calendar.get("sprint_length_days"), 14)
        return sprints * sprint_days

    @staticmethod
    def day(value: str | None) -> date | None:
        return BaselineForecast.day(value)
