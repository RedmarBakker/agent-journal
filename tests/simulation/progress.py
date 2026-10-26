from tests.simulation.trace_entry import TraceEntry

STUCK_STEPS = 40


class Progress:
    """The agent gets somewhere: forty of its actions in a row all refused, whatever they were, is a livelock no single remedy shows."""

    def violated(self, trace: list[TraceEntry]) -> str:
        refused = 0
        for entry in (entry for entry in trace if entry.actor == "agent"):
            refused = refused + 1 if entry.refused else 0
            if refused >= STUCK_STEPS:
                return f"the agent's last {refused} actions up to second {entry.second} were all refused: {', '.join(entry.nudges) or 'no line said why'}"
        return ""
