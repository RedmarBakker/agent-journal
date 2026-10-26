import random

from tests.simulation.world import World

PLACES = 3


class OrchestratorPolicy:
    """The orchestrator's way: it answers the user's messages first, takes in finished work next, oldest first, hands every open task it has a place for to a worker, and writes nothing itself."""

    def action(self, world: World, chance: random.Random, told: tuple[tuple[str, str], ...]) -> str:
        if world.unread_messages:
            return "answer"
        if world.workers_done:
            return "merge"
        if world.open_tasks and len(world.workers_out) < PLACES:
            return "dispatch"
        return "read" if world.workers_out else "stop"
