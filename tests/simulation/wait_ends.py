from tests.simulation.trace_entry import TraceEntry

WAIT_STATES = ("waiting", "external_wait", "wait")
LIMIT_SECONDS = 30 * 60


class WaitEnds:
    """A wait on top of the agent's stack ends: one held for half an hour of simulated time while the agent kept acting is a wait nothing lifts."""

    def violated(self, trace: list[TraceEntry]) -> str:
        began = None
        for entry in (entry for entry in trace if entry.actor == "agent"):
            waiting = bool(entry.stack) and entry.stack[-1] in WAIT_STATES
            began = (began if began is not None else entry.second) if waiting else None
            if began is not None and entry.second - began > LIMIT_SECONDS:
                return f"the agent sat in {entry.stack[-1]} from second {began} to {entry.second}"
        return ""
