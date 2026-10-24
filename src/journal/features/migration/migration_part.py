from typing import ClassVar

from journal.features.migration.support.migration_data import MigrationData
from journal.events.data_source import DataSource


class MigrationPart(DataSource[MigrationData]):
    """The migration feature's part of the feature data."""

    name: ClassVar[str] = "migration"
