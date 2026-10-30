from dataclasses import FrozenInstanceError

import pytest

from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from tests.lab.lab_scenario import LabScenario
from tests.lab.scenario_loader import ScenarioLoader
from tests.test_features import booted
from tests.user_settings import USER_CALLER


@pytest.fixture(scope="module")
def boot():
    return booted


def test_scenario_loads_as_an_approved_plan_and_expectations_read_task_rows(app, tmp_path):
    path = tmp_path / "ship-feature.toml"
    path.write_text(
        '''id = "ship-feature"
title = "Ship a feature with a data migration"
business_type = "software_company"
goal = "Ship a tested feature with a safe data migration."

[[phases]]
id = "define"
title = "Define the feature"
complete_when = "The feature scope is accepted."
[[phases.tasks]]
id = "specify"
title = "Specify the feature"
brief = "Record the required product behavior."
domain = "product"
size = 2
prerequisites = []

[[phases]]
id = "build"
title = "Build the feature"
complete_when = "The feature is implemented and tested."
[[phases.tasks]]
id = "implement"
title = "Implement the feature"
brief = "Build the accepted feature and migration."
domain = "engineering"
size = 5
prerequisites = ["specify"]

[[phases]]
id = "release"
title = "Verify the release"
complete_when = "The release is ready for approval."
[[phases.tasks]]
id = "verify"
title = "Verify the release"
brief = "Check the migration and release behavior."
domain = "quality"
size = 3
prerequisites = ["implement"]

[[events]]
minute = 5
kind = "customer_message"
payload = { text = "Please include the migration status." }
[[events]]
minute = 15
kind = "external_wait_released"
payload = { target = "customer_data_export" }
[[events]]
minute = 20
kind = "role_failure"
payload = { role = "software_engineer" }
[[events]]
minute = 30
kind = "user_away"
payload = { duration_minutes = 120 }
[[events]]
minute = 40
kind = "approval_action"
payload = { role = "release_manager", action = "production_deployment" }

[[expected]]
id = "release_verified"
description = "The release verification task is complete."
table = "tasks"
target = "verify"
field = "state"
equals = "completed"

[rubric]
version = "business-plan-v1"
[[rubric.criteria]]
id = "handoff_traceability"
weight = 100
expectations = ["release_verified"]

[budget]
simulated_minutes = 300
[budget.real_caps]
state = "owner_pending"
''',
        encoding="utf-8",
    )

    scenario = LabScenario.read(path)
    with pytest.raises(FrozenInstanceError):
        scenario.goal = "Changed"
    with pytest.raises(TypeError):
        scenario.phases[1]["tasks"][0]["size"] = 8
    assert [event["minute"] for event in scenario.events] == [5, 15, 20, 30, 40]
    assert scenario.budget["real_caps"]["state"] == "owner_pending"

    loaded = ScenarioLoader(app).load(scenario)
    plans, tasks = app.container.get(Plans), app.container.get(Tasks)
    plan = plans.find(loaded["plan_id"])
    assert plan.state == PlanState.APPROVED
    with app.container.get(Scope).environment(plan.environment_id):
        assert [phase.title for phase in plans.plan_phases(plan)] == [phase["title"] for phase in scenario.phases]
        for phase, phase_spec in zip(plans.plan_phases(plan), scenario.phases, strict=True):
            assert [task.row_id for task in plans.phase_tasks(phase)] == [loaded["task_ids"][item["id"]] for item in phase_spec["tasks"]]
        assert scenario.phases[1]["tasks"][0]["prerequisites"] == ("specify",)

        expectation = scenario.expected[0]
        task_id = loaded["task_ids"][expectation.target]
        assert tasks.find(task_id).state == TaskState.OPEN
        assert not expectation.matches(tasks.find(task_id))
        outcome = app.run_without_server(["task", "complete", str(task_id), "--how", "Release verified"], USER_CALLER)
        assert outcome.code == 0, outcome.error
        assert expectation.matches(tasks.find(task_id))
