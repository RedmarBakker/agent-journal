from journal.config import Config
from journal.db.migration_failures import MigrationFailures
from journal.features.seed import Seed
from journal.models.notice import Notice
from journal.repositories.environments import Environments
from journal.repositories.notices import Notices
from journal.repositories.scope import Scope
from journal.support.actor import Actor

LOG_FILE = "migrations.log"


class MigrationFailureNotice(Seed):
    """A migration that failed at boot is written to the runtime log and shown in every environment as a notice naming it and saying it will be tried again at the next start."""

    def __init__(self, failures: MigrationFailures, notices: Notices, environments: Environments, scope: Scope, config: Config) -> None:
        self.failures, self.notices, self.environments, self.scope, self.config = failures, notices, environments, scope, config

    def run(self) -> None:
        if not self.failures.rows:
            return
        log = self.config.home / "runtime" / LOG_FILE
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a") as file:
            file.write("\n".join(self.failures.lines()) + "\n")
        for environment in self.environments.all():
            with self.scope.environment(environment.row_id):
                for failure in self.failures.rows:
                    self.notices.save(Notice(environment_id=environment.row_id, title=f"Migration {failure.number} failed and was rolled back; it will be tried again at the next start: {failure.error}", tone="warn"), Actor.system())
