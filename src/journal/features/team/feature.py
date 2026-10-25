from journal.support.card_family import CardFamily
from journal.support.mark_kind import MarkKind
from journal.support.mark_kinds import WORK
from journal.support.card_kind import CardKind
from journal.features.feature import Feature
from journal.features.support.service import Service
from journal.features.team.support.team_data import TeamData
from journal.features.team.support.team_data_reader import TeamDataReader
from journal.features.team.team_conduct import TeamConduct
from journal.features.team.commands.session_command import SessionCommand
from journal.features.team.commands.team_command import TeamCommand
from journal.features.team.jobs.team_chat_files import TeamChatFiles
from journal.features.team.seeds.single_team_chat import SingleTeamChat
from journal.features.team.listeners.colleague_write_guard import ColleagueWriteGuard
from journal.features.team.listeners.environment_owner_record import EnvironmentOwnerRecord
from journal.features.team.listeners.sync_moment_cards import SyncMomentCards
from journal.features.team.team_part import TeamPart
from journal.features.team.team_nudges import TeamNudges


class TeamFeature(Feature[TeamData]):
    name = TeamPart.name
    card_families = (CardFamily("team", "Team", "warn", WORK),)
    card_kinds = (MarkKind(CardKind.CONFLICTS, "Your edits a colleague's newer edit replaced", "team", main=False, shown=False),)
    title = "Team"
    help = "A journal shared with a team through its server: joining it, inviting people, the team's devices and how the sync stands."
    commands = (TeamCommand, SessionCommand)
    listeners = (EnvironmentOwnerRecord, ColleagueWriteGuard, SyncMomentCards)
    jobs = (TeamChatFiles,)
    seeds = (SingleTeamChat,)
    data = (TeamDataReader,)
    conduct = (TeamConduct,)
    services = (Service("sync", "sync_service", "/health"),)

    nudges = (TeamNudges.UPGRADE_NEEDED,)
