from collections.abc import Callable

from tests.simulation.trace_entry import TraceEntry


class Shrinker:
    """Cuts a failing run's agent actions to the fewest that still break its invariant: each action is taken out in turn and the rest replayed from the same seed and time, and kept out while the invariant still fails."""

    def __init__(self, replay: Callable[[list[str]], list[TraceEntry]], invariant) -> None:
        self.replay, self.invariant = replay, invariant

    def shrunk(self, actions: list[str]) -> list[str]:
        i = 0
        while i < len(actions):
            fewer = actions[:i] + actions[i + 1:]
            if self.invariant.violated(self.replay(fewer)):
                actions = fewer
            else:
                i += 1
        return actions
