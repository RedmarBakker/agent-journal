from pathlib import Path

from journal.engine.agent_launcher import AgentLauncher
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.plans_options import PlansOptions
from journal.features.workers.organization_options import OrganizationOptions
from journal.models.plan_state import PlanState
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from tests.lab.business_type import BusinessType
from tests.lab.design import Design
from tests.lab.lab_journal import LabJournal
from tests.lab.lab_scenario import LabScenario
from tests.lab.run_request import RunRequest
from tests.lab.scenario_pin import ScenarioPin


def request(root: Path, home: Path) -> RunRequest:
    return RunRequest(
        "a" * 32, 1, ScenarioPin("production_incident", "software_company", "1", "b" * 64, 420),
        Design.from_mapping("baseline", {"workers.cost_cap_dollars": 3}), 17, "VoidProvider", "synthetic-tier",
        "c" * 40, "d" * 40, "1", 420, root, home, root / "result.json",
    )


def test_a_lab_journal_loads_its_scenario_and_replaces_process_and_openrig_calls(tmp_path, monkeypatch):
    scenario = LabScenario.read(Path(__file__).parent / "scenarios/software_company/production_incident.toml")
    business = BusinessType.read(Path(__file__).parent / "business_types/software_company.toml")
    run = request(tmp_path / "root", tmp_path / "home")

    with LabJournal(run, scenario, business, monkeypatch) as lab:
        settings = lab.app.container.get(SettingRows)
        assert settings.option(PlansOptions.PLAN_AGENTS) is True
        assert settings.option(OrganizationOptions.FOLDER) == str(lab.organization_folder)
        plan = lab.app.container.get(Plans).find(lab.scenario_rows["plan_id"])
        assert plan.state is PlanState.APPROVED
        assert len(lab.scenario_rows["task_ids"]) == 3
        assert (lab.organization_folder / "domains" / "engineering" / "AGENTS.md").is_file()

        launcher = lab.app.container.get(AgentLauncher)
        assert launcher.start_in_worktree("scenario-plan", "claude", ("--resume", "native"), ("repo",)) > 0
        assert lab.launches[-1] == {
            "environment": "scenario-plan", "agent": "claude", "resume": ("--resume", "native"), "repositories": ("repo",),
        }
        runtime = lab.app.container.get(SeatRuntime)
        assert runtime.version() == "0.7.5"
        assert lab.seats.calls[-1] == ("--version",)
        spec = lab.root / ".journal" / "runtime" / "rigs" / "simulated" / "rig.yaml"
        runtime.start_rig(spec)
        assert runtime.rig_exists("simulated")
        assert ("up", str(spec), "--json") in lab.seats.calls
