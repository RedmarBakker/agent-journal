import random

from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.simulation.builder_policy import BuilderPolicy
from tests.simulation.careless_policy import CarelessPolicy
from tests.simulation.main_agent import AGENT, MainAgent
from tests.simulation.orchestrator_policy import OrchestratorPolicy
from tests.simulation.scenario import Scenario
from tests.simulation.simulator import Simulator
from tests.simulation.solo_policy import SoloPolicy
from tests.simulation.trace_entry import TraceEntry
from tests.simulation.user_actor import UserActor
from tests.simulation.worker_actor import WorkerActor
from tests.simulation.world import World

STEP_SECONDS = 30
POLICIES = {"builder": BuilderPolicy, "orchestrator": OrchestratorPolicy, "solo": SoloPolicy, "careless": CarelessPolicy}


class ScenarioRun:
    """One scenario played on one journal from one seed: every simulated half minute the user may write, finished workers clock out, and the main agent plays its policy's action; the trace it returns is the same for the same seed."""

    def __init__(self, simulator: Simulator, scenario: Scenario, seed: int) -> None:
        self.simulator, self.scenario, self.seed = simulator, scenario, seed

    def played(self) -> list[TraceEntry]:
        world, trace = World(), []
        self.prepared(world)
        agent = MainAgent(self.simulator, POLICIES[self.scenario.policy](), random.Random(self.seed), self.scenario.worker_seconds)
        user = UserActor(self.simulator, random.Random(self.seed + 1), self.scenario.user_messages_hourly, STEP_SECONDS)
        workers = WorkerActor(self.simulator)
        for step in range(self.scenario.minutes * 60 // STEP_SECONDS):
            self.simulator.advance(STEP_SECONDS)
            second = (step + 1) * STEP_SECONDS
            written = user.maybe_message()
            if written is not None:
                trace.append(TraceEntry(second, "user", "message", written.is_refused(), written.nudges))
            for number, seen in workers.finished(world):
                trace.append(TraceEntry(second, f"worker {number}", "clock-out", seen.answer[0] != 0, seen.nudges))
            action, seen = agent.act(world)
            trace.append(TraceEntry(second, "agent", action, seen.is_refused() or seen.answer[0] not in (0, 200), seen.nudges))
        return trace

    def prepared(self, world: World) -> None:
        settings = self.simulator.app.container.get(SettingRows)
        settings.set("workers.mode", self.scenario.mode, Actor.user(1))
        self.simulator.hook("SessionStart")
        self.simulator.run(["environment", "overview"], AGENT)
        for n in range(1, self.scenario.tasks + 1):
            self.simulator.run(["task", "create", f"part {n}", "--brief", f"1. part {n} is written"], Caller.user("main"))
            world.open_tasks.append(n)
