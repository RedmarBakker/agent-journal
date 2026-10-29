from dataclasses import dataclass, field

from journal.features.organization.support.contracts import Contracts


@dataclass(frozen=True)
class OrganizationData:
    """The organization feature's reading: the domains and Roles the folder holds now, and every version read before, so a job asks for the version it began on."""

    contracts: Contracts
    history: dict[str, Contracts] = field(default_factory=dict)

    def contracts_at(self, version: str) -> Contracts:
        return self.history.get(version, self.contracts)
