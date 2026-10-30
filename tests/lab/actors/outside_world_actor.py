import random

from journal.support.caller import Caller
from tests.lab.behaviour_profile import BehaviourProfile
from tests.observation import Observation
from tests.simulation.simulator import Simulator

PARTIES = frozenset({"customer", "insurer", "court"})


class OutsideWorldActor:
    """Customers, insurers and courts answer journal questions after a seeded delay."""

    def __init__(self, simulator: Simulator, profile: BehaviourProfile, seed: int, environment: str = "main") -> None:
        if profile.agent_kind != "outside_world":
            raise ValueError("the outside world needs an outside-world behaviour profile")
        self.simulator, self.profile, self.chance = simulator, profile, random.Random(seed)
        self.caller = Caller.user(environment)
        self.pending: list[tuple[float, int, int, str, str]] = []
        self.sequence = 0
        self.released: list[tuple[str, int, str]] = []

    def answer_after(self, question: int, answer: str, party: str) -> float:
        if party not in PARTIES:
            raise ValueError(f"unknown outside-world party: {party}")
        due = self.simulator.source.seconds() + self.profile.job_seconds(self.chance)
        self.sequence += 1
        self.pending.append((due, self.sequence, question, answer, party))
        return due

    def release_due(self) -> tuple[Observation, ...]:
        now = self.simulator.source.seconds()
        due = sorted(entry for entry in self.pending if entry[0] <= now)
        self.pending = [entry for entry in self.pending if entry[0] > now]
        answered = []
        for _, _, question, answer, party in due:
            result = self.simulator.run(["question", "answer", str(question), answer], self.caller)
            self.released.append((party, question, answer))
            answered.append(result)
        return tuple(answered)
