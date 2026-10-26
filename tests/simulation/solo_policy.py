import random

from tests.simulation.world import World


class SoloPolicy:
    """The solo way: it does every task itself and never hands one out."""

    def action(self, world: World, chance: random.Random) -> str:
        return "write" if world.open_tasks else "stop"
