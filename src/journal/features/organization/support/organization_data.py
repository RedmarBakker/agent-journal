from dataclasses import dataclass, field

from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.role_approvals import RoleApprovals


@dataclass(frozen=True)
class OrganizationData:
    """The organization contract, its prior versions and approvals, and the handoffs or Role work waiting for this agent."""

    contracts: Contracts
    history: dict[str, Contracts] = field(default_factory=dict)
    approvals: RoleApprovals | None = None
    waiting_plan_handoff: tuple[int, str] | None = None
    unread_handoff: bool = False
    role_work_waiting_for_check: tuple[tuple[int, int], ...] = ()

    def contracts_at(self, version: str) -> Contracts:
        return self.history.get(version, self.contracts)
