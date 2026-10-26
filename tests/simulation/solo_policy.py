import random

from tests.simulation.world import World


class SoloPolicy:
    """The solo way: it answers the user's messages first, does every task itself and never hands one out."""

    def action(self, world: World, chance: random.Random, told: tuple[tuple[str, str], ...]) -> str:
        if world.unread_messages:
            return "answer"
        return "write" if world.open_tasks else "stop"
