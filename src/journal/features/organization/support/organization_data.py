from dataclasses import dataclass

from journal.features.organization.support.contracts import Contracts


@dataclass(frozen=True)
class OrganizationData:
    """The organization feature's reading: the domains and Roles the folder holds, which a state or a conduct asks for a Role instead of asking the loader."""

    contracts: Contracts
