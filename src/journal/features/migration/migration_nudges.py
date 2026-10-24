from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class MigrationNudges:
    PENDING_MIGRATION = Nudge("migration", "version_3_not_brought_across", "a version 3 journal waits in .journal/version-3", "the user brings it across; never start it yourself", repeat=Timeout.seconds(0))
