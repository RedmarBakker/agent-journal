import random

from tests.simulation.nudge_response import NudgeResponse
from tests.simulation.world import World

FOLLOW_DELAY_STEPS = 6


class KnownPolicy:
    """An agent that follows the lines it is told at a set rate, from a random of its own seeded with the run's seed plus three: a line followed is answered by its action on the row it names three simulated minutes later (six steps), a refusal by the remedy it names, one pending answer serving every line that asks the same of the same row, and otherwise the base policy plays."""

    def __init__(self, base, follow_rate: float, seed: int) -> None:
        self.base, self.follow_rate, self.chance = base, follow_rate, random.Random(seed + 3)
        self.step, self.due = 0, []

    def action(self, world: World, chance: random.Random, told: tuple[tuple[str, str], ...]) -> str:
        self.step += 1
        for key, line in told:
            self.heard(key, line, line in world.refusal_lines)
        ready = [entry for entry in self.due if entry[0] <= self.step]
        if not ready:
            return self.base.action(world, chance, told)
        self.due.remove(ready[0])
        _, response, row, remedy = ready[0]
        return self.taken(world, response, row, remedy)

    def heard(self, key: str, line: str, is_refusal: bool) -> None:
        response, remedy = NudgeResponse.action(key), NudgeResponse.remedy(line) if is_refusal else []
        taken = (response or "remedy", NudgeResponse.named_row(response, line), remedy)
        if (response or remedy) and taken not in [entry[1:] for entry in self.due] and self.chance.random() < self.follow_rate:
            self.due.append((self.step + FOLLOW_DELAY_STEPS, *taken))

    @staticmethod
    def taken(world: World, response: str, row: int, remedy: list[str]) -> str:
        for rows in (world.workers_done, world.open_tasks):
            if row in rows:
                rows.insert(0, rows.pop(rows.index(row)))
        if remedy:
            world.remedies.append(remedy)
        return response
