from journal.engine.nudge import Nudge


class MigrationNudges:
    PENDING_MIGRATION = Nudge("migration", "version_3_not_brought_across", "a version 3 journal waits in .journal/version-3", "the user brings it across; never start it yourself", repeat_interval=0)
