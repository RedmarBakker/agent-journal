import random

from tests.simulation.world import World


class BuilderPolicy:
    """The builder's way: it answers the user's messages first, writes most of the work itself, takes one task at a time, and hands a task to a worker only now and then."""

    def action(self, world: World, chance: random.Random) -> str:
        if world.unread_messages:
            return "answer"
        if world.workers_done:
            return "merge"
        if world.open_tasks and chance.random() < 0.15 and not world.workers_out:
            return "dispatch"
        return "write" if world.open_tasks else "stop"
