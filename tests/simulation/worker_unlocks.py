from tests.simulation.trace_entry import TraceEntry


class WorkerUnlocks:
    """A worker's writes are never left paused: no worker is still locked for a rebase once a step has ended."""

    def violated(self, trace: list[TraceEntry]) -> str:
        locked = next((entry for entry in trace if any(state.endswith(":locked") for state in entry.workers)), None)
        return f"after {locked.actor}'s {locked.action} at second {locked.second} a worker's writes stayed locked: {', '.join(locked.workers)}" if locked else ""
