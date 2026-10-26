import random

from journal.features.workers.support.tool_use_counts import ToolUseCounts
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.simulation.builder_policy import BuilderPolicy
from tests.simulation.careless_policy import CarelessPolicy
from tests.simulation.heredoc_policy import HeredocPolicy
from tests.simulation.job_lengths import JobLengths
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
POLICIES = {"builder": BuilderPolicy, "orchestrator": OrchestratorPolicy, "solo": SoloPolicy, "careless": CarelessPolicy, "heredoc": HeredocPolicy}


class ScenarioRun:
    """One scenario played on one journal from one seed: every simulated half minute the user may write, finished workers clock out, the clock ticks once a minute as the journal's does, tasks arrive and the work mode switches at the minutes the scenario names, and the main agent plays its policy's action, a merge sending back the clashed workers the scenario names; the trace it returns is the same for the same seed, and the fitness and load it read after each agent action are kept as samples for scoring again."""

    def __init__(self, simulator: Simulator, scenario: Scenario, seed: int, policy) -> None:
        self.simulator, self.scenario, self.seed, self.policy = simulator, scenario, seed, policy
        self.samples: list[Sample] = []

    def played(self) -> list[TraceEntry]:
        world, trace = World(), []
        self.prepared(world)
        agent = MainAgent(self.simulator, self.policy, random.Random(self.seed), JobLengths(self.scenario, random.Random(self.seed + 4)), self.scenario.send_backs)
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
            if second % 60 == 0:
                self.minute_passed(world, second // 60)
            action, seen = agent.act(world)
            trace.append(self.entry(second, "agent", action, seen))
            if action == "merge" and self.scenario.clashes_per_merge:
                for number in list(world.workers_done[:self.scenario.clashes_per_merge]):
                    trace.append(self.entry(second, f"worker {number}", "clash", workers.clashes(world, number, "a merge landed under its branch")))
            self.sampled(second)
        return trace

    def minute_passed(self, world: World, minute: int) -> None:
        self.simulator.tick()
        for _ in range(sum(count for at, count in self.scenario.arrivals if at == minute)):
            self.task_created(world)
        if self.scenario.switch_minute and minute == self.scenario.switch_minute:
            self.simulator.app.container.get(SettingRows).set("workers.mode", self.scenario.switch_mode, Actor.user(1))

    def task_created(self, world: World) -> None:
        n = world.next_task
        world.next_task += 1
        self.simulator.run(["task", "create", f"part {n}", "--brief", f"1. part {n} is written"], Caller.user("main"))
        world.open_tasks.append(n)

    def sampled(self, second: int) -> None:
        agent = self.simulator.app.container.get(Agents).session_agent("s1")
        self.samples.append(Sample(second, ToolUseCounts.counted(agent), agent.work_queue.rho, agent.measures, agent.band))

    @staticmethod
    def entry(second: int, actor: str, action: str, seen) -> TraceEntry:
        status = seen.answer[0] if isinstance(seen.answer, tuple) and seen.answer else 0
        return TraceEntry(second, actor, action, status not in (0, 200), seen.nudges, seen.stack, status, seen.skipped, seen.workers)

    def prepared(self, world: World) -> None:
        settings = self.simulator.app.container.get(SettingRows)
        settings.set("workers.mode", self.scenario.mode, Actor.user(1))
        self.simulator.hook("SessionStart")
        self.simulator.run(["environment", "overview"], AGENT)
        for _ in range(self.scenario.tasks):
            self.task_created(world)
