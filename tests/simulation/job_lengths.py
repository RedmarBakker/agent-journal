import random

from tests.simulation.scenario import Scenario


class JobLengths:
    """How long a simulated worker's job runs, in seconds: drawn from the scenario's deciles in minutes with the run's seeded random, the fixed length when it gives none."""

    def __init__(self, scenario: Scenario, chance: random.Random) -> None:
        self.scenario, self.chance = scenario, chance

    def seconds(self) -> float:
        if not self.scenario.job_minutes:
            return self.scenario.worker_seconds
        return self.seconds_from(self.scenario.job_minutes, self.chance)

    @staticmethod
    def seconds_from(minutes: tuple[float, ...], chance: random.Random) -> float:
        return chance.choice(minutes) * 60
