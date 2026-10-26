from tests.simulation.trace_entry import TraceEntry

STOPS = 6


class StopReleases:
    """A run of refused stops ends: the engine's own release after five refused stops, or journal stuck, lets the agent stop by the sixth."""

    def violated(self, trace: list[TraceEntry]) -> str:
        refused = 0
        for entry in (entry for entry in trace if entry.actor == "agent" and entry.action == "stop"):
            refused = refused + 1 if entry.refused else 0
            if refused >= STOPS:
                return f"{refused} stops in a row were refused, the last at second {entry.second}: nothing released the agent"
        return ""
