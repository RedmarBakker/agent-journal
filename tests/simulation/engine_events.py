import random

from journal.support.caller import Caller
from tests.observation import Observation
from tests.simulation.main_agent import AGENT
from tests.simulation.simulator import Simulator

USER = Caller.user("main")
EVENTS = ("compaction", "pause", "resume", "question", "answer", "restart", "approval")


class EngineEvents:
    """The moments of the engine itself a simulation plays among the work, drawn from its own seeded random: a compaction, the agent paused and resumed, a question asked and answered, the session restarted, and a plan approved by the user."""

    def __init__(self, simulator: Simulator, chance: random.Random, share: float) -> None:
        self.simulator, self.chance, self.share = simulator, chance, share
        self.questions, self.plans, self.session = 0, 0, 1

    def maybe_event(self) -> tuple[str, Observation] | None:
        if self.chance.random() >= self.share:
            return None
        event = self.chance.choice(EVENTS)
        return event, getattr(self, f"{event}_event")()

    def compaction_event(self) -> Observation:
        self.simulator.hook("PreCompact", session=f"s{self.session}")
        return self.simulator.hook("SessionStart", session=f"s{self.session}", source="compact")

    def pause_event(self) -> Observation:
        return self.simulator.run(["panic", "paused"], AGENT)

    def resume_event(self) -> Observation:
        return self.simulator.run(["panic", "pop"], AGENT)

    def question_event(self) -> Observation:
        self.questions += 1
        return self.simulator.run(["question", "ask", f"Which way, {self.questions}?", "--options", "the agent goes left", "the agent goes right"], AGENT)

    def answer_event(self) -> Observation:
        if not self.questions:
            return self.question_event()
        return self.simulator.run(["question", "answer", str(self.questions), "the agent goes left"], USER)

    def restart_event(self) -> Observation:
        self.session += 1
        return self.simulator.hook("SessionStart", session=f"s{self.session}", source="startup")

    def approval_event(self) -> Observation:
        self.plans += 1
        n = str(self.plans)
        self.simulator.run(["plan", "create", f"plan {n}", "--brief", "a goal"], USER)
        self.simulator.run(["plan", "add", n, f"step of plan {n}", "--brief", "1. done"], USER)
        self.simulator.run(["plan", "ready", n], USER)
        return self.simulator.run(["plan", "approve", n], USER)
