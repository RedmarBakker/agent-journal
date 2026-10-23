from typing import ClassVar

from journal.events.data_source import DataSource


class BranchEnvironments(DataSource[dict]):
    """The branches the other environments with a running agent work on, each with that environment; none when no feature reads them."""

    name: ClassVar[str] = "branch_environments"

    @classmethod
    def missing(cls) -> dict:
        return {}
