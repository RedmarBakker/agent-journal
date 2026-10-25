from journal.features.feature import Feature
from journal.features.health.commands.supervision_command import SupervisionCommand
from journal.features.health.health_options import HealthOptions
from journal.features.health.jobs.database_backup import DatabaseBackup


class Health(Feature):
    name = "health"
    title = "Health and backups"
    help = "The supervisor asks the journal every few seconds whether it is well, and starts it again after so many misses in a row; the journal answers unwell when an environment's hooks stop reaching it or it cannot open a file or read its database. The journal also writes an online copy of its database every so many minutes to .journal/backups-watch, keeping the newest few."
    options = (HealthOptions.CHECK_SECONDS, HealthOptions.ANSWER_SECONDS, HealthOptions.MISSES, HealthOptions.BOOT_SECONDS, HealthOptions.BACKUP_MINUTES, HealthOptions.BACKUP_COUNT)
    jobs = (DatabaseBackup,)
    commands = (SupervisionCommand,)
