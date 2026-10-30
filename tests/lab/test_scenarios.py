from collections import Counter
from pathlib import Path

import pytest

from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from tests.lab.lab_scenario import EVENT_KINDS, LabScenario
from tests.lab.scenario_loader import ScenarioLoader
from tests.test_features import booted

SCENARIOS = tuple(sorted((Path(__file__).parent / "scenarios").glob("*/*.toml")))
BUSINESS_TYPES = frozenset({"accountancy_firm", "dental_practice", "fleet_operator", "law_firm", "sales_company", "software_company"})
EXPECTED_TABLES = frozenset({"tasks", "artifacts", "approvals", "hub_audits"})


@pytest.fixture(scope="module")
def boot():
    return booted


def test_scenario_library_has_three_scenarios_per_business_type():
    counts = Counter(path.parent.name for path in SCENARIOS)

    assert len(SCENARIOS) == 18
    assert set(counts) == BUSINESS_TYPES
    assert set(counts.values()) == {3}


@pytest.mark.parametrize("path", SCENARIOS, ids=lambda path: f"{path.parent.name}-{path.stem}")
def test_scenario_loads_as_an_approved_plan_with_unmet_expectations(app, path):
    scenario = LabScenario.read(path)
    assert scenario.business_type == path.parent.name
    assert {event["kind"] for event in scenario.events} == EVENT_KINDS
    assert {expectation.table for expectation in scenario.expected} == EXPECTED_TABLES
    assert any(event["kind"] == "user_away" and event["payload"]["duration_minutes"] == 120 for event in scenario.events)

    plans = app.container.get(Plans)
    scope = app.container.get(Scope)
    environments = app.container.get(Environments)
    main = environments.lookup("main")
    with scope.environment(main.id):
        assert not plans.all()

    loaded = ScenarioLoader(app).load(scenario)
    plan = plans.find(loaded["plan_id"])
    assert plan.state == PlanState.APPROVED

    tasks = app.container.get(Tasks)
    with scope.environment(plan.environment_id):
        phases = plans.plan_phases(plan)
        assert [phase.title for phase in phases] == [phase["title"] for phase in scenario.phases]
        for phase, phase_spec in zip(phases, scenario.phases, strict=True):
            assert [task.row_id for task in plans.phase_tasks(phase)] == [loaded["task_ids"][item["id"]] for item in phase_spec["tasks"]]
        for expectation in scenario.expected:
            row = None
            if expectation.table == "tasks":
                row = tasks.find(loaded["task_ids"][expectation.target])
                assert row.state == TaskState.OPEN
            assert not expectation.matches(row), expectation.id
