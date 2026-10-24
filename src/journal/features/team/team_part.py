from typing import ClassVar

from journal.features.team.support.team_data import TeamData
from journal.events.data_source import DataSource


class TeamPart(DataSource[TeamData]):
    """The team feature's part of the feature data."""

    name: ClassVar[str] = "team"
