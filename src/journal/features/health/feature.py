from journal.features.feature import Feature
from journal.features.health.commands.supervision_command import SupervisionCommand
from journal.features.health.health_options import HealthOptions
from journal.features.health.listeners.bypass_notice import BypassNotice
from journal.features.health.jobs.database_backup import DatabaseBackup
from journal.features.health.health_conduct import HealthConduct
from journal.features.health.health_nudges import HealthNudges
from journal.features.health.health_part import HealthPart
from journal.features.health.support.unchecked_work import UncheckedWork
from journal.features.health.support.unchecked_work_reader import UncheckedWorkReader


class Health(Feature[UncheckedWork]):
    name = HealthPart.name
    title = "Health and backups"
    help = "The supervisor asks the journal every few seconds whether it is well, and starts it again after so many misses in a row; the journal answers unwell when an environment's hooks stop reaching it or it cannot open a file or read its database. The journal also writes an online copy of its database every so many minutes to .journal/backups-watch, keeping the newest few. A hook or a shell command that went around a journal that did not answer is named once in the chat at the journal's next answer, and the agent is told in one line to check them."
    options = (HealthOptions.CHECK_SECONDS, HealthOptions.ANSWER_SECONDS, HealthOptions.MISSES, HealthOptions.BOOT_SECONDS, HealthOptions.BACKUP_MINUTES, HealthOptions.BACKUP_COUNT)
    listeners = (BypassNotice,)
    jobs = (DatabaseBackup,)
    commands = (SupervisionCommand,)
    nudges = (HealthNudges.UNCHECKED_WORK,)
    data = (UncheckedWorkReader,)
    conduct = (HealthConduct,)
