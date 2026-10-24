from typing import ClassVar

from journal.events.data_source import DataSource


class StopRefusalsPart(DataSource[int]):
    """The engine's part of the feature data: how many of the agent's stops were refused in a row, with no tool use and no message of the user's between them."""

    name: ClassVar[str] = "stop_refusals"

    @classmethod
    def missing(cls) -> int:
        return 0
