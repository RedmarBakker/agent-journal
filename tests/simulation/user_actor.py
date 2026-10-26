import random

from journal.support.caller import Caller
from tests.observation import Observation
from tests.simulation.simulator import Simulator

USER = Caller.user("main")


class UserActor:
    """The simulated user: sends a message at the scenario's rate, drawn each step from its own seeded random."""

    def __init__(self, simulator: Simulator, chance: random.Random, messages_hourly: float, step_seconds: int) -> None:
        self.simulator, self.chance = simulator, chance
        self.share = messages_hourly * step_seconds / 3600

    def maybe_message(self) -> Observation | None:
        if self.chance.random() >= self.share:
            return None
        return self.simulator.run(["message", "send", "how is it going?"], USER)
