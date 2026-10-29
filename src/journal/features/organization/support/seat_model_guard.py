from journal.features.organization.support.role import Role


class SeatModelGuard:
    """Whether a seat runs on the model its Role's contract names: the model OpenRig observed on the seat must be, or contain, the contract's for its provider, and when it is not the line says the seat is to be restarted on the contract's, never left running on another."""

    @staticmethod
    def mismatch(role: Role, provider: str, observed: str) -> str:
        wanted = role.models.for_provider(provider)
        if wanted.lower() in observed.lower():
            return ""
        return f"the seat of the Role {role.id} runs on {observed or 'no model'} but its contract names {wanted} on {provider}: restart it on {wanted}"
