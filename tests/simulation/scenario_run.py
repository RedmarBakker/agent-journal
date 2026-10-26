import random

from journal.features.workers.support.tool_use_counts import ToolUseCounts
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.simulation.builder_policy import BuilderPolicy
from tests.simulation.careless_policy import CarelessPolicy
from tests.simulation.engine_events import EngineEvents
from tests.simulation.main_agent import AGENT, MainAgent
from tests.simulation.orchestrator_policy import OrchestratorPolicy
from tests.simulation.sample import Sample
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
    """One scenario played on one journal from one seed: every simulated half minute the user may write, finished workers clock out, and the main agent plays its policy's action; the trace it returns is the same for the same seed, and the fitness and load it read after each agent action are kept as samples for scoring again."""

    def __init__(self, simulator: Simulator, scenario: Scenario, seed: int, policy) -> None:
        self.simulator, self.scenario, self.seed, self.policy = simulator, scenario, seed, policy
        self.samples: list[Sample] = []

    def played(self) -> list[TraceEntry]:
        world, trace = World(), []
        self.prepared(world)
        agent = MainAgent(self.simulator, self.policy, random.Random(self.seed), self.scenario.worker_seconds)
        user = UserActor(self.simulator, random.Random(self.seed + 1), self.scenario.user_messages_hourly, STEP_SECONDS)
        workers = WorkerActor(self.simulator)
        engine = EngineEvents(self.simulator, random.Random(self.seed + 2), self.scenario.engine_events_hourly * STEP_SECONDS / 3600)
        for step in range(self.scenario.minutes * 60 // STEP_SECONDS):
            self.simulator.advance(STEP_SECONDS)
            second = (step + 1) * STEP_SECONDS
            written = user.maybe_message()
            if written is not None:
                world.unread_messages += 1
                trace.append(self.entry(second, "user", "message", written))
            for number, seen in workers.finished(world):
                trace.append(self.entry(second, f"worker {number}", "clock-out", seen))
            happened = engine.maybe_event()
            if happened is not None:
                trace.append(self.entry(second, "engine", happened[0], happened[1]))
            action, seen = agent.act(world)
            trace.append(self.entry(second, "agent", action, seen))
            self.sampled(second)
        return trace

    def sampled(self, second: int) -> None:
        agent = self.simulator.app.container.get(Agents).session_agent("s1")
        self.samples.append(Sample(second, ToolUseCounts.counted(agent), agent.load.rho))

    @staticmethod
    def entry(second: int, actor: str, action: str, seen) -> TraceEntry:
        status = seen.answer[0] if isinstance(seen.answer, tuple) and seen.answer else 0
        return TraceEntry(second, actor, action, status not in (0, 200), seen.nudges, seen.stack, status, seen.skipped, seen.workers)

    def prepared(self, world: World) -> None:
        settings = self.simulator.app.container.get(SettingRows)
        settings.set("workers.mode", self.scenario.mode, Actor.user(1))
        self.simulator.hook("SessionStart")
        self.simulator.run(["environment", "overview"], AGENT)
        for n in range(1, self.scenario.tasks + 1):
            self.simulator.run(["task", "create", f"part {n}", "--brief", f"1. part {n} is written"], Caller.user("main"))
            world.open_tasks.append(n)
