from tests.simulation.trace_entry import TraceEntry


class NoFaults:
    """The journal never fails under a run: no answer of 500 or more, and no deferred work skipped."""

    def violated(self, trace: list[TraceEntry]) -> str:
        fault = next((entry for entry in trace if entry.status >= 500 or entry.skipped), None)
        if fault is None:
            return ""
        return f"at second {fault.second} {fault.actor}'s {fault.action} " + (f"was answered {fault.status}" if fault.status >= 500 else f"left {fault.skipped} pieces of deferred work skipped")
