from tests.simulation.trace_entry import TraceEntry


class PrimaryRoleRoute:
    """A Domain agent routes to its contract's primary Role."""

    def __init__(self, domain_id: str, primary_role: str) -> None:
        self.actor, self.primary_role = f"domain:{domain_id}", primary_role

    def violated(self, trace: list[TraceEntry]) -> str:
        fault = next((
            entry for entry in trace
            if entry.actor == self.actor and entry.action.startswith("route:")
            and entry.action != f"route:{self.primary_role}"
        ), None)
        if fault is None:
            return ""
        return (
            f"{fault.actor} routed {fault.action.removeprefix('route:')} instead of {self.primary_role} "
            f"at second {fault.second}"
        )
