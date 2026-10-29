import random

from tests.simulation.world import World


class HandingBuilderPolicy:
    """A builder that writes none of its own code: it answers the user, takes in finished work, and hands its open tasks to one worker at a time, so open tasks stay waiting for it to write; the case its own-code-share measure is for."""

    def action(self, world: World, chance: random.Random, told: tuple[tuple[str, str], ...]) -> str:
        if world.unread_messages:
            return "answer"
        if world.workers_done:
            return "merge"
        if world.open_tasks and not world.workers_out:
            return "dispatch"
        return "read" if world.workers_out else "stop"
