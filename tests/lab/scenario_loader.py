from collections.abc import Mapping

from journal.app import App
from journal.models.plan_mode import PlanMode
from tests.lab.lab_scenario import LabScenario
from tests.user_settings import USER_CALLER


class ScenarioLoader:
    def __init__(self, app: App) -> None:
        self.app = app

    def load(self, scenario: LabScenario, mode: PlanMode | None = None,
             organization_domain_map: Mapping[str, str] | None = None) -> dict[str, object]:
        domain_map = self.require_organization_domain_map(scenario, mode, organization_domain_map)
        plan_id = self.row_id(self.command(["plan", "create", scenario.title, "--brief", scenario.goal]), "plan")
        phase_numbers = {}
        task_ids = {}
        for number, phase in enumerate(scenario.phases, 1):
            self.command(["plan", "phase", str(plan_id), phase["title"], "--when", phase["complete_when"]])
            phase_numbers[phase["id"]] = number
            for task in phase["tasks"]:
                words = ["plan", "add", str(plan_id), task["title"], "--brief", task["brief"], "--phase", str(number)]
                if mode is PlanMode.ORGANIZATION:
                    words.extend(["--domain", domain_map[task["domain"]]])
                task_ids[task["id"]] = self.row_id(self.command(words), "task")
        if mode is not None:
            self.command(["plan", "mode", str(plan_id), mode.value])
        self.command(["plan", "ready", str(plan_id)])
        self.command(["plan", "approve", str(plan_id)])
        return {"plan_id": plan_id, "phase_numbers": phase_numbers, "task_ids": task_ids}

    @staticmethod
    def require_organization_domain_map(scenario: LabScenario, mode: PlanMode | None,
                                        domain_map: Mapping[str, str] | None) -> Mapping[str, str]:
        if mode is not PlanMode.ORGANIZATION:
            return {}
        if domain_map is None:
            raise ValueError("organization plan scenarios need a mapping to the pinned organization")
        domains = {task["domain"] for phase in scenario.phases for task in phase["tasks"]}
        missing = sorted(domains - domain_map.keys())
        if missing:
            raise ValueError(f"scenario domains lack mappings to the pinned organization: {', '.join(missing)}")
        return domain_map

    def command(self, words: list[str]) -> str:
        outcome = self.app.run_without_server(words, USER_CALLER)
        if outcome.code:
            raise RuntimeError(outcome.error or outcome.text)
        return outcome.text.strip()

    @staticmethod
    def row_id(output: str, noun: str) -> int:
        words = output.splitlines()[0].split()
        if len(words) < 2 or words[0] != noun or not words[1].isdecimal():
            raise RuntimeError(f"journal did not return a {noun} row id: {output}")
        return int(words[1])
