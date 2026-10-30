import os
from pathlib import Path

from journal.config import Config
from journal.engine.agent_launcher import AgentLauncher
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.plans_options import PlansOptions
from journal.features.workers.organization_options import OrganizationOptions
from journal.models.setting import Setting
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from tests.lab.business_type import BusinessType
from tests.lab.design import Design
from tests.lab.lab_scenario import LabScenario
from tests.lab.organization_builder import OrganizationBuilder
from tests.lab.run_request import RunRequest
from tests.lab.scenario_loader import ScenarioLoader
from tests.lab.simulated_seats import SimulatedSeats
from tests.main_journal import main_journal
from tests.simulation.simulator import Simulator
from tests.stories.builder.void_provider import VoidProvider
from tests.user_settings import user_set


class LabJournal:
    """Build one isolated in-process journal for a simulated lab run."""

    def __init__(self, request: RunRequest, scenario: LabScenario, business_type: BusinessType, monkeypatch) -> None:
        if scenario.id != request.scenario.name or scenario.business_type != business_type.id:
            raise ValueError("the run request, scenario and business type must identify the same run")
        self.root, self.launches = request.root, []
        self.root.mkdir(parents=True, exist_ok=True)
        request.home.mkdir(parents=True, exist_ok=True)
        if (self.root / ".journal").exists():
            raise ValueError("a simulated run needs a fresh journal root")
        monkeypatch.setenv("HOME", str(request.home))
        monkeypatch.setattr(Config, "status_home", property(lambda _config: request.home / ".journal" / "status"))
        self.organization_folder = OrganizationBuilder().build(business_type, self.root / "organization")
        self.app = main_journal(Config(self.root, port=0))
        self.app.container.get(SettingRows).save(
            Setting(environment_id=0, key="features.skills", value=False), Actor.system()
        )
        self.set_design(request.design)
        user_set(self.app, OrganizationOptions.FOLDER.key, str(self.organization_folder))
        user_set(self.app, PlansOptions.PLAN_AGENTS.key, True)
        self.seats = SimulatedSeats()
        monkeypatch.setattr(AgentLauncher, "start_in_worktree", self.start_in_worktree)
        monkeypatch.setattr(SeatRuntime, "run", self.seats.run)
        self.app.runtime().start()
        try:
            self.simulator = Simulator(self.app, monkeypatch, VoidProvider.name)
            self.scenario_rows = ScenarioLoader(self.app).load(scenario)
        except BaseException:
            self.app.runtime().stop()
            raise
        self.closed = False

    def set_design(self, design: Design) -> None:
        for key, value in design.settings:
            if key not in {OrganizationOptions.FOLDER.key, PlansOptions.PLAN_AGENTS.key}:
                user_set(self.app, key, "" if value is None else value)

    def start_in_worktree(self, environment: str, agent: str, resume: tuple[str, ...], repositories: tuple[str, ...] | None = None) -> int:
        self.launches.append({
            "environment": environment,
            "agent": agent,
            "resume": resume,
            "repositories": repositories,
        })
        return os.getpid()

    def close(self) -> None:
        if not self.closed:
            self.app.runtime().stop()
            self.closed = True

    def __enter__(self) -> "LabJournal":
        return self

    def __exit__(self, _kind, _failure, _traceback) -> None:
        self.close()
