from tests.simulation.trace_entry import TraceEntry


class PrimaryRoleRoute:
    """A Domain sends a job to the primary Role named by its matching routing rule."""

    def __init__(self, domain_id: str, primary_role: str) -> None:
        self.domain_id, self.primary_role = domain_id, primary_role

    def violated(self, trace: list[TraceEntry]) -> str:
        actor = f"domain:{self.domain_id}"
        for entry in trace:
            if entry.actor != actor or not entry.action.startswith("route:"):
                continue
            role = entry.action.removeprefix("route:")
            if role != self.primary_role:
                return (
                    f"the {self.domain_id} Domain routed to {role}, not its primary Role {self.primary_role} "
                    f"at second {entry.second}"
                )
        return ""
