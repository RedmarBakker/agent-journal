from datetime import date, timedelta


class CriticalPath:
    """Projects earliest dates and slack from task durations and declared prerequisites."""

    def project(self, as_of: str | None, tasks: list[dict], graph: dict) -> dict:
        rows = sorted((dict(row) for row in tasks), key=lambda row: row["task_id"])
        task_ids = {row["task_id"] for row in rows}
        edges = self.edges(graph.get("edges", ()), task_ids)
        external = self.external_conditions(graph.get("external_conditions", ()), edges)
        independent = self.independent_groups(task_ids, edges)
        result = {"status": "structural", "basis": "structural dependency graph", "as_of": as_of,
                  "p50_finish": None, "duration_days": None, "critical_path_task_ids": [], "critical_task_ids": [],
                  "independent_groups": independent, "edges": edges, "external_conditions": external,
                  "unknown_reasons": [], "tasks": [self.unknown_row(row) for row in rows]}
        if not rows:
            return {**result, "status": "empty", "basis": "no remaining tasks", "unknown_reasons": []}
        start = self.day(as_of)
        reasons = self.unknown_reasons(rows, start, external)
        if reasons:
            return {**result, "unknown_reasons": reasons}
        order, prerequisites, successors = self.order(task_ids, edges)
        earliest = self.earliest(order, prerequisites, rows)
        latest = self.latest(order, successors, rows, earliest)
        duration = max(earliest[task_id][1] for task_id in task_ids)
        critical = sorted(task_id for task_id in task_ids if latest[task_id][0] == earliest[task_id][0])
        path = self.longest_path(order, prerequisites, earliest, duration)
        projected = [self.timed_row(row, start, earliest, latest) for row in rows]
        return {**result, "status": "estimated", "basis": "shared P50 task durations", "p50_finish": (start + timedelta(days=duration)).isoformat(),
                "duration_days": duration, "critical_path_task_ids": path, "critical_task_ids": critical,
                "unknown_reasons": [], "tasks": projected}

    @staticmethod
    def edges(rows, task_ids: set[int]) -> list[dict]:
        return sorted(({"task_id": row["task_id"], "prerequisite_id": row["prerequisite_id"],
                        "kind": row["kind"], "external": bool(row.get("external")) or row["prerequisite_id"] not in task_ids}
                       for row in rows if row["task_id"] in task_ids),
                      key=lambda row: (row["task_id"], row["prerequisite_id"], row["kind"]))

    @staticmethod
    def external_conditions(rows, edges: list[dict]) -> list[dict]:
        indexed = {(row["task_id"], row["prerequisite_id"], row["kind"]): row for row in rows}
        conditions = []
        for edge in edges:
            if not edge["external"]:
                continue
            status = indexed.get((edge["task_id"], edge["prerequisite_id"], edge["kind"]), {}).get("status", "unresolved")
            conditions.append({**edge, "status": status})
        return conditions

    @staticmethod
    def unknown_row(row: dict) -> dict:
        return {"task_id": row["task_id"], "p50_duration_days": row.get("p50_duration_days"),
                "earliest_start": None, "earliest_finish": None, "latest_start": None,
                "latest_finish": None, "slack_days": None, "critical": False}

    @staticmethod
    def unknown_reasons(rows: list[dict], as_of: date | None, external: list[dict]) -> list[str]:
        reasons = []
        if as_of is None:
            reasons.append("forecast date")
        if any(not isinstance(row.get("p50_duration_days"), int) or isinstance(row.get("p50_duration_days"), bool)
               or row["p50_duration_days"] < 0 for row in rows):
            reasons.append("P50 task duration")
        if any(row["status"] != "resolved" for row in external):
            reasons.append("external condition")
        return reasons

    @staticmethod
    def order(task_ids: set[int], edges: list[dict]) -> tuple[list[int], dict[int, list[int]], dict[int, list[int]]]:
        prerequisites = {task_id: [] for task_id in task_ids}
        successors = {task_id: [] for task_id in task_ids}
        for edge in edges:
            if edge["external"]:
                continue
            prerequisites[edge["task_id"]].append(edge["prerequisite_id"])
            successors[edge["prerequisite_id"]].append(edge["task_id"])
        incoming = {task_id: len(values) for task_id, values in prerequisites.items()}
        ready = sorted(task_id for task_id, count in incoming.items() if count == 0)
        order = []
        while ready:
            current = ready.pop(0)
            order.append(current)
            for dependent in sorted(successors[current]):
                incoming[dependent] -= 1
                if incoming[dependent] == 0:
                    ready.append(dependent)
                    ready.sort()
        if len(order) != len(task_ids):
            raise ValueError("critical path graph contains a prerequisite cycle")
        return order, prerequisites, successors

    @staticmethod
    def earliest(order: list[int], prerequisites: dict[int, list[int]], rows: list[dict]) -> dict[int, tuple[int, int]]:
        durations = {row["task_id"]: row["p50_duration_days"] for row in rows}
        result = {}
        for task_id in order:
            start = max((result[prerequisite][1] for prerequisite in prerequisites[task_id]), default=0)
            result[task_id] = (start, start + durations[task_id])
        return result

    @staticmethod
    def latest(order: list[int], successors: dict[int, list[int]], rows: list[dict],
               earliest: dict[int, tuple[int, int]]) -> dict[int, tuple[int, int]]:
        durations = {row["task_id"]: row["p50_duration_days"] for row in rows}
        project_finish = max(finish for _start, finish in earliest.values())
        result = {}
        for task_id in reversed(order):
            finish = min((result[successor][0] for successor in successors[task_id]), default=project_finish)
            result[task_id] = (finish - durations[task_id], finish)
        return result

    @staticmethod
    def longest_path(order: list[int], prerequisites: dict[int, list[int]],
                     earliest: dict[int, tuple[int, int]], duration: int) -> list[int]:
        paths = {}
        for task_id in order:
            parents = [parent for parent in prerequisites[task_id] if earliest[parent][1] == earliest[task_id][0]]
            prefix = min((paths[parent] for parent in parents), default=())
            paths[task_id] = (*prefix, task_id)
        return list(min(paths[task_id] for task_id in order if earliest[task_id][1] == duration))

    @staticmethod
    def timed_row(row: dict, start: date, earliest: dict[int, tuple[int, int]],
                  latest: dict[int, tuple[int, int]]) -> dict:
        task_id = row["task_id"]
        early_start, early_finish = earliest[task_id]
        late_start, late_finish = latest[task_id]
        slack = late_start - early_start
        return {"task_id": task_id, "p50_duration_days": row["p50_duration_days"],
                "earliest_start": (start + timedelta(days=early_start)).isoformat(),
                "earliest_finish": (start + timedelta(days=early_finish)).isoformat(),
                "latest_start": (start + timedelta(days=late_start)).isoformat(),
                "latest_finish": (start + timedelta(days=late_finish)).isoformat(),
                "slack_days": slack, "critical": slack == 0}

    @staticmethod
    def independent_groups(task_ids: set[int], edges: list[dict]) -> list[list[int]]:
        connected = set()
        for edge in edges:
            connected.add(edge["task_id"])
            if edge["prerequisite_id"] in task_ids:
                connected.add(edge["prerequisite_id"])
        return [[task_id] for task_id in sorted(task_ids - connected)]

    @staticmethod
    def day(value: str | None) -> date | None:
        if not isinstance(value, str):
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
