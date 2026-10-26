import random

from tests.simulation.world import World


class ScriptedPolicy:
    """An agent playing a recorded list of actions in order, as a shrunk trace replays them; once the list runs out it only reads."""

    def __init__(self, actions: list[str]) -> None:
        self.actions = list(actions)

    def action(self, world: World, chance: random.Random) -> str:
        return self.actions.pop(0) if self.actions else "read"
