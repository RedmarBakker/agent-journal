from journal.features.feature import Feature
from journal.features.updates.commands.update_command import UpdateCommand
from journal.features.updates.jobs.restart_check import RestartCheck
from journal.features.updates.listeners.release_check import ReleaseCheck
from journal.features.updates.listeners.supervisor_upgrade import SupervisorUpgrade
from journal.features.updates.listeners.session_restart_close import SessionRestartClose
from journal.features.updates.listeners.launch_takeover_notice import LaunchTakeoverNotice
from journal.features.updates.support.release_source import REPOSITORY
from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope
from journal.features.updates.support.release_notes import ReleaseNotes
from journal.features.updates.support.release_notes_reader import ReleaseNotesReader
from journal.features.updates.updates_conduct import UpdatesConduct
from journal.features.updates.seeds.version_change import VersionChange
from journal.features.updates.seeds.supervisor_check import SupervisorCheck
from journal.features.updates.updates_part import UpdatesPart
from journal.features.updates.updates_nudges import UpdatesNudges
from journal.features.updates.updates_options import UpdatesOptions


class Updates(Feature[ReleaseNotes]):
    name = UpdatesPart.name
    title = "Updates"
    help = "Finds the newest release of this version of the journal on GitHub, as often as you set, and installs it when you say so or, if you switch that on, by itself."
    options = (UpdatesOptions.REPOSITORY, UpdatesOptions.BRANCH, UpdatesOptions.AUTO, UpdatesOptions.CHECK_INTERVAL)
    listeners = (ReleaseCheck, SupervisorUpgrade, SessionRestartClose, LaunchTakeoverNotice)
    seeds = (VersionChange, SupervisorCheck)
    nudges = (UpdatesNudges.RELEASE_MESSAGES, UpdatesNudges.LAUNCH_TAKEOVER)
    data = (ReleaseNotesReader,)
    conduct = (UpdatesConduct,)
    jobs = (RestartCheck,)
    commands = (UpdateCommand,)
