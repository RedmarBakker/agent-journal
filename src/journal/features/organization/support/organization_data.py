from dataclasses import dataclass, field

from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.role_approvals import RoleApprovals


@dataclass(frozen=True)
class OrganizationData:
    """The domains and Roles in the organization folder, its prior versions, and any plan task waiting for its Domain handoff."""

    contracts: Contracts
    history: dict[str, Contracts] = field(default_factory=dict)
    approvals: RoleApprovals | None = None
    waiting_plan_handoff: tuple[int, str] | None = None

    def contracts_at(self, version: str) -> Contracts:
        return self.history.get(version, self.contracts)
