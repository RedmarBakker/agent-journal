import random

from tests.simulation.world import World

ACTIONS = ("write", "read", "dispatch", "merge", "stop", "message")


class CarelessPolicy:
    """An agent taking any legal action at random, for the search for stuck states: whatever the journal offers must still lead somewhere."""

    def action(self, world: World, chance: random.Random) -> str:
        return chance.choice(ACTIONS)
