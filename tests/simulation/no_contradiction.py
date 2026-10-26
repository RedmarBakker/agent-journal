from tests.simulation.opposed_lines import OpposedLines
from tests.simulation.trace_entry import TraceEntry

WINDOW_SECONDS = 600


class NoContradiction:
    """Two lines that ask opposite things never reach the agent within ten simulated minutes of each other, the time an agent takes to act on the first."""

    def violated(self, trace: list[TraceEntry]) -> str:
        said = [(entry.second, key) for entry in trace for key in entry.nudges]
        for index, (second, key) in enumerate(said):
            clash = next(((later, other) for later, other in said[index + 1:] if later - second <= WINDOW_SECONDS and OpposedLines.opposed(key, other)), None)
            if clash:
                return f"the agent was told {key} at second {second} and {clash[1]} at second {clash[0]}, within {WINDOW_SECONDS // 60} minutes"
        return ""
