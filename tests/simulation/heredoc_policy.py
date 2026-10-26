import random

from tests.simulation.builder_policy import BuilderPolicy
from tests.simulation.world import World


class HeredocPolicy:
    """The builder's way with every line of code written through the shell, heredocs into files and commits, never the editor."""

    def __init__(self) -> None:
        self.builder = BuilderPolicy()

    def action(self, world: World, chance: random.Random, told: tuple[tuple[str, str], ...]) -> str:
        chosen = self.builder.action(world, chance, told)
        return "shell_write" if chosen == "write" else chosen
