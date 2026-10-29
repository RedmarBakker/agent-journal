from journal.features.organization.support.contract_reader import ContractReader
from journal.features.organization.support.contracts import Contracts


class Organization:
    """The funnel the rest of journal asks for the organization's domains and Roles: read from the folder on first use and again after a reload, never cached anywhere else."""

    def __init__(self, reader: ContractReader) -> None:
        self.reader, self.loaded = reader, None

    def contracts(self) -> Contracts:
        if self.loaded is None:
            self.loaded = self.reader.read()
        return self.loaded

    def reload(self) -> Contracts:
        self.loaded = self.reader.read()
        return self.loaded
