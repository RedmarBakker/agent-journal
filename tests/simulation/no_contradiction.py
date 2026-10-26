from tests.simulation.trace_entry import TraceEntry

OPPOSED = (
    ("workers.load_critical", "workers.builder_handover_budget"),
    ("workers.load_critical", "workers.dispatch_while_busy"),
    ("workers.worker_place_free", "workers.load_critical"),
)


class NoContradiction:
    """Two lines that ask opposite things never reach the agent in one step, such as the load asking it to hand work out while the builder's budget asks it to write the work itself."""

    def violated(self, trace: list[TraceEntry]) -> str:
        for entry in trace:
            said = set(entry.nudges)
            pair = next((pair for pair in OPPOSED if set(pair) <= said), None)
            if pair:
                return f"at second {entry.second} the agent was told both {pair[0]} and {pair[1]}"
        return ""
