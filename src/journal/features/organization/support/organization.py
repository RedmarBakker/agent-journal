from journal.features.organization.support.contract_reader import ContractReader
from journal.features.organization.support.contracts import Contracts


class Organization:
    """The funnel the rest of journal asks for the organization's domains and Roles: read from the folder on first use and again after a reload, never cached anywhere else; every version read is remembered by its digest, so a job that began on one keeps that version while a later job begins on the changed folder."""

    def __init__(self, reader: ContractReader) -> None:
        self.reader, self.loaded, self.history = reader, None, {}

    def contracts(self) -> Contracts:
        return self.loaded if self.loaded is not None else self.reload()

    def reload(self) -> Contracts:
        self.loaded = self.reader.read()
        self.history[self.loaded.version] = self.loaded
        return self.loaded

    def at(self, version: str) -> Contracts:
        return self.history.get(version, self.contracts())

    def is_stale(self) -> bool:
        return self.loaded is not None and self.reader.has_changed(self.loaded)
