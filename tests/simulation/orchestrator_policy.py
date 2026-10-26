import random

from tests.simulation.world import World

PLACES = 3


class OrchestratorPolicy:
    """The orchestrator's way: it takes in finished work first, oldest first, hands every open task it has a place for to a worker, and writes nothing itself."""

    def action(self, world: World, chance: random.Random) -> str:
        if world.workers_done:
            return "merge"
        if world.open_tasks and len(world.workers_out) < PLACES:
            return "dispatch"
        return "read" if world.workers_out else "stop"
