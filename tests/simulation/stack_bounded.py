from tests.simulation.trace_entry import TraceEntry

DEPTH = 8


class StackBounded:
    """The agent's stack of states stays shallow: deeper than eight layers is states pushed and never popped."""

    def violated(self, trace: list[TraceEntry]) -> str:
        deep = next((entry for entry in trace if len(entry.stack) > DEPTH), None)
        return f"the agent's stack reached {len(deep.stack)} layers at second {deep.second}: {', '.join(deep.stack)}" if deep else ""
