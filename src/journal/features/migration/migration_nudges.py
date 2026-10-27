from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class MigrationNudges:
    PENDING_MIGRATION = Nudge("migration", "version_3_not_brought_across", "a version 3 journal is in .journal/version-3", "only the user brings it across; never start it", repeat=Timeout.seconds(0))
