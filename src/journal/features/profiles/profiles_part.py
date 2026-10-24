from typing import ClassVar

from journal.features.profiles.support.profiles_data import ProfilesData
from journal.events.data_source import DataSource


class ProfilesPart(DataSource[ProfilesData]):
    """The profiles feature's part of the feature data."""

    name: ClassVar[str] = "profiles"
