import random

from tests.simulation.world import World


class ScriptedPolicy:
    """An agent playing a recorded list of actions in order, as a shrunk trace replays them, keeping what it was told before each; once the list runs out it only reads."""

    def __init__(self, actions: list[str]) -> None:
        self.actions = list(actions)
        self.told: list[tuple[tuple[str, str], ...]] = []

    def action(self, world: World, chance: random.Random, told: tuple[tuple[str, str], ...]) -> str:
        self.told.append(told)
        return self.actions.pop(0) if self.actions else "read"
