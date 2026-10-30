import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from tests.lab.business_type import freeze
from tests.lab.expectation import Expectation
from tests.lab.scenario_rubric import CRITERIA, RUBRIC_VERSION

SIZES = frozenset({1, 2, 3, 5, 8, 13})
EVENT_KINDS = frozenset({"customer_message", "external_wait_released", "role_failure", "user_away", "approval_action"})


@dataclass(frozen=True)
class LabScenario:
    id: str
    title: str
    business_type: str
    goal: str
    phases: tuple[Mapping[str, object], ...]
    events: tuple[Mapping[str, object], ...]
    expected: tuple[Expectation, ...]
    rubric: Mapping[str, object]
    budget: Mapping[str, object]

    @classmethod
    def read(cls, path: Path) -> "LabScenario":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        phases = cls.records(data, "phases")
        events = cls.records(data, "events")
        expected = cls.records(data, "expected")
        rubric = data.get("rubric")
        if not isinstance(rubric, dict):
            raise ValueError("scenario rubric must be a table")
        budget = data.get("budget")
        if not isinstance(budget, dict):
            raise ValueError("scenario budget must be a table")
        return cls(
            data["id"],
            data["title"],
            data["business_type"],
            data["goal"],
            tuple(cast(Mapping[str, object], freeze(phase)) for phase in phases),
            tuple(cast(Mapping[str, object], freeze(event)) for event in events),
            tuple(Expectation.read(item) for item in expected),
            cast(Mapping[str, object], freeze(rubric)),
            cast(Mapping[str, object], freeze(budget)),
        )

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value.strip() for value in (self.id, self.title, self.business_type, self.goal)):
            raise ValueError("a scenario needs an id, title, business type and goal")
        phase_ids, task_ids, domains, dependencies = [], [], set(), {}
        for phase in self.phases:
            if not isinstance(phase, Mapping):
                raise ValueError("scenario phases must be tables")
            phase_ids.append(self.text(phase, "id", "phase"))
            self.text(phase, "title", "phase")
            self.text(phase, "complete_when", "phase")
            tasks = phase.get("tasks")
            if not isinstance(tasks, tuple) or not tasks:
                raise ValueError(f"phase {phase['id']} needs at least one task")
            for task in tasks:
                if not isinstance(task, Mapping):
                    raise ValueError(f"phase {phase['id']} tasks must be tables")
                task_id = self.text(task, "id", "task")
                if task_id in task_ids:
                    raise ValueError("scenario task ids must be unique")
                task_ids.append(task_id)
                self.text(task, "title", "task")
                self.text(task, "brief", "task")
                domain = self.text(task, "domain", "task")
                size = task.get("size")
                if type(size) is not int or size not in SIZES:
                    raise ValueError(f"task {task['id']} size must be one of {', '.join(map(str, sorted(SIZES)))}")
                prerequisites = task.get("prerequisites")
                if not isinstance(prerequisites, tuple) or any(not isinstance(item, str) for item in prerequisites):
                    raise ValueError(f"task {task['id']} prerequisites must be a list of task ids")
                if task["id"] in prerequisites or len(set(prerequisites)) != len(prerequisites):
                    raise ValueError(f"task {task['id']} has a repeated or self prerequisite")
                domains.add(domain)
                dependencies[task_id] = prerequisites
        if len(set(phase_ids)) != len(phase_ids):
            raise ValueError("scenario phase ids must be unique")
        if len(domains) < 3:
            raise ValueError("a scenario must cross at least three domains")
        unknown = {item for prerequisites in dependencies.values() for item in prerequisites} - set(task_ids)
        if unknown:
            raise ValueError(f"scenario prerequisites name unknown tasks: {', '.join(sorted(unknown))}")
        self.no_cycles(dependencies)
        self.validate_events()
        self.validate_expectations(set(task_ids))
        self.validate_rubric()
        self.validate_budget()

    @staticmethod
    def records(data: Mapping[str, object], key: str) -> list[dict[str, object]]:
        records = data.get(key)
        if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
            raise ValueError(f"scenario {key} must be an array of tables")
        return records

    @staticmethod
    def text(data: Mapping[str, object], key: str, kind: str) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"scenario {kind} needs {key}")
        return value

    def no_cycles(self, dependencies: Mapping[str, tuple[str, ...]]) -> None:
        visiting, visited = set(), set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise ValueError(f"scenario prerequisites contain a cycle at {task_id}")
            if task_id in visited:
                return
            visiting.add(task_id)
            for prerequisite in dependencies[task_id]:
                visit(prerequisite)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in dependencies:
            visit(task_id)

    def validate_events(self) -> None:
        if not self.events:
            raise ValueError("a scenario needs at least one injected event")
        minutes = []
        for event in self.events:
            if not isinstance(event, Mapping):
                raise ValueError("scenario events must be tables")
            minute, kind = event.get("minute"), event.get("kind")
            if type(minute) is not int or minute < 0 or kind not in EVENT_KINDS:
                raise ValueError("scenario events need a non-negative minute and a supported kind")
            minutes.append(minute)
        if minutes != sorted(minutes):
            raise ValueError("scenario events must be listed by minute")

    def validate_expectations(self, task_ids: set[str]) -> None:
        if not self.expected or len({item.id for item in self.expected}) != len(self.expected):
            raise ValueError("a scenario needs uniquely named expectations")
        for item in self.expected:
            if item.table == "tasks" and item.target not in task_ids:
                raise ValueError(f"expectation {item.id} names unknown task {item.target}")

    def validate_rubric(self) -> None:
        if self.rubric.get("version") != RUBRIC_VERSION:
            raise ValueError(f"scenario rubric version must be {RUBRIC_VERSION}")
        criteria = self.rubric.get("criteria")
        if not isinstance(criteria, tuple) or not criteria:
            raise ValueError("scenario rubric needs criteria")
        expectation_tables = {item.id: item.table for item in self.expected}
        criterion_ids, covered, total_weight = set(), set(), 0
        for criterion in criteria:
            if not isinstance(criterion, Mapping):
                raise ValueError("scenario rubric criteria must be tables")
            criterion_id = self.text(criterion, "id", "rubric criterion")
            if criterion_id not in CRITERIA or criterion_id in criterion_ids:
                raise ValueError(f"scenario rubric has an unknown or repeated criterion: {criterion_id}")
            criterion_ids.add(criterion_id)
            weight = criterion.get("weight")
            if type(weight) is not int or weight <= 0:
                raise ValueError(f"rubric criterion {criterion_id} needs a positive whole-number weight")
            total_weight += weight
            expectations = criterion.get("expectations")
            if not isinstance(expectations, tuple) or not expectations or any(not isinstance(item, str) for item in expectations):
                raise ValueError(f"rubric criterion {criterion_id} needs expectation ids")
            if len(set(expectations)) != len(expectations):
                raise ValueError(f"rubric criterion {criterion_id} repeats an expectation")
            if covered.intersection(expectations):
                raise ValueError("scenario rubric assigns an expectation to more than one criterion")
            for expectation_id in expectations:
                if expectation_id not in expectation_tables:
                    raise ValueError(f"rubric criterion {criterion_id} names an unknown expectation: {expectation_id}")
                if expectation_tables[expectation_id] not in CRITERIA[criterion_id]["tables"]:
                    raise ValueError(f"rubric criterion {criterion_id} cannot score expectation {expectation_id}")
            covered.update(expectations)
        if total_weight != 100:
            raise ValueError("scenario rubric criterion weights must sum to 100")
        if covered != set(expectation_tables):
            raise ValueError("scenario rubric criteria must cover every scenario expectation")

    def validate_budget(self) -> None:
        simulated = self.budget.get("simulated_minutes")
        caps = self.budget.get("real_caps")
        if type(simulated) is not int or simulated <= 0:
            raise ValueError("scenario simulated_minutes must be a positive integer")
        if not isinstance(caps, Mapping) or caps.get("state") != "owner_pending" or len(caps) != 1:
            raise ValueError("real caps must remain explicitly owner_pending until selected in question 30")
