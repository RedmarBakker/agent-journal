import math
import random

from journal.features.organization.support.role_approvals import APPROVE_ANSWER
from journal.support.caller import Caller
from tests.observation import Observation
from tests.simulation.simulator import Simulator


class UserActor:
    """The simulated user: sends messages at its scenario rate, answers approvals and waits, and may be away."""

    def __init__(self, simulator: Simulator, chance: random.Random, messages_hourly: float, step_seconds: int, environment: str = "main") -> None:
        self.simulator, self.chance = simulator, chance
        self.share = messages_hourly * step_seconds / 3600
        self.caller, self.absent_until = Caller.user(environment), 0.0

    def maybe_message(self) -> Observation | None:
        if self.is_away() or self.chance.random() >= self.share:
            return None
        return self.simulator.run(["message", "send", "how is it going?"], self.caller)

    def answer(self, question: int, answer: str) -> Observation | None:
        if self.is_away():
            return None
        return self.simulator.run(["question", "answer", str(question), answer], self.caller)

    def approve(self, question: int) -> Observation | None:
        return self.answer(question, APPROVE_ANSWER)

    def away_for(self, minutes: float) -> None:
        if minutes <= 0 or not math.isfinite(minutes):
            raise ValueError("an absence lasts a positive number of minutes")
        starts = max(self.absent_until, self.simulator.source.seconds())
        self.absent_until = starts + minutes * 60

    def return_from_absence(self) -> None:
        self.absent_until = self.simulator.source.seconds()

    def is_away(self) -> bool:
        return self.simulator.source.seconds() < self.absent_until
