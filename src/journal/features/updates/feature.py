from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import JOURNAL
from journal.support.card_type import CardType
from journal.features.feature import Feature
from journal.features.updates.commands.update_command import UpdateCommand
from journal.features.updates.jobs.restart_check import RestartCheck
from journal.features.updates.listeners.release_check import ReleaseCheck
from journal.features.updates.listeners.supervisor_upgrade import SupervisorUpgrade
from journal.features.updates.listeners.session_restart_close import SessionRestartClose
from journal.features.updates.listeners.launch_takeover_notice import LaunchTakeoverNotice
from journal.features.updates.listeners.boot_failure_notice import BootFailureNotice
from journal.features.updates.support.release_source import REPOSITORY
from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope
from journal.features.updates.support.release_notes import ReleaseNotes
from journal.features.updates.support.release_notes_reader import ReleaseNotesReader
from journal.features.updates.updates_conduct import UpdatesConduct
from journal.features.updates.seeds.version_change import VersionChange
from journal.features.updates.seeds.migration_failure_notice import MigrationFailureNotice
from journal.features.updates.seeds.supervisor_check import SupervisorCheck
from journal.features.updates.updates_part import UpdatesPart
from journal.features.updates.updates_nudges import UpdatesNudges
from journal.features.updates.updates_options import UpdatesOptions


class Updates(Feature[ReleaseNotes]):
    name = UpdatesPart.name
    card_families = (CardFamily("updates", "Updates", "bolt", JOURNAL),)
    card_types = (CardTypeEntry(CardType.UPDATES, "The journal server replaced by a newer launch", "updates"),)
    title = "Updates"
    help = "Finds the newest release of this version of the journal on GitHub, as often as you set, and installs it when you say so or, if you switch that on, by itself."
    options = (UpdatesOptions.REPOSITORY, UpdatesOptions.BRANCH, UpdatesOptions.AUTO, UpdatesOptions.CHECK_INTERVAL, UpdatesOptions.BOOT_SECONDS, UpdatesOptions.WINDOW_MINORS)
    listeners = (ReleaseCheck, SupervisorUpgrade, SessionRestartClose, LaunchTakeoverNotice, BootFailureNotice)
    seeds = (VersionChange, SupervisorCheck, MigrationFailureNotice)
    nudges = (UpdatesNudges.RELEASE_MESSAGES, UpdatesNudges.LAUNCH_TAKEOVER)
    data = (ReleaseNotesReader,)
    conduct = (UpdatesConduct,)
    jobs = (RestartCheck,)
    commands = (UpdateCommand,)
