from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.features.migration.migration_nudges import MigrationNudges
from journal.features.migration.migration_part import MigrationPart


class MigrationConduct(Conduct):
    """The migration feature's conduct in every state: at a start, a version 3 journal waiting to be migrated is mentioned."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        return self.none(MigrationNudges.PENDING_MIGRATION.create()) if event.data.part(MigrationPart).version_3_waiting else self.none()
