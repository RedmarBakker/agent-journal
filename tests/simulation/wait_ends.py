from tests.simulation.trace_entry import TraceEntry

LIMITS = {"waiting": 60 * 60, "external_wait": 30 * 60, "wait": 30 * 60, "compacting": 5 * 60, "reading_overview": 10 * 60}


class WaitEnds:
    """A state that holds the agent ends: each has its longest stay in simulated time (a question an hour, a wait half an hour, a compaction five minutes, the overview after one ten), and one past it while the agent kept acting is held by nothing that lifts it; a paused agent may stay as long as the user leaves it."""

    def violated(self, trace: list[TraceEntry]) -> str:
        began = None
        for entry in (entry for entry in trace if entry.actor == "agent"):
            waiting = bool(entry.stack) and entry.stack[-1] in LIMITS
            began = (began if began is not None else entry.second) if waiting else None
            if began is not None and entry.second - began > LIMITS[entry.stack[-1]]:
                return f"the agent sat in {entry.stack[-1]} from second {began} to {entry.second}"
        return ""
