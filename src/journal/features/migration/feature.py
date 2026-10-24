from journal.features.feature import Feature
from journal.features.migration.migration_conduct import MigrationConduct
from journal.features.migration.support.migration_data_reader import MigrationDataReader
from journal.features.migration.support.migration_data import MigrationData
from journal.features.migration.migration_part import MigrationPart
from journal.features.migration.migration_nudges import MigrationNudges


class MigrationFeature(Feature[MigrationData]):
    name = MigrationPart.name
    title = "Migration from version 3"
    fixed = True
    help = "A version 3 journal the installer kept in .journal/version-3 is offered to the user to bring across; the agent is told it is there and never starts it."

    nudges = (MigrationNudges.PENDING_MIGRATION,)
    data = (MigrationDataReader,)
    conduct = (MigrationConduct,)

