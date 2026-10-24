from journal.features.feature import Feature
from journal.features.team.support.team_data import TeamData
from journal.features.team.support.team_data_reader import TeamDataReader
from journal.features.team.team_conduct import TeamConduct
from journal.features.team.commands.team_command import TeamCommand
from journal.features.team.jobs.team_chat_files import TeamChatFiles
from journal.features.team.seeds.single_team_chat import SingleTeamChat
from journal.features.team.listeners.colleague_write_guard import ColleagueWriteGuard
from journal.features.team.listeners.environment_owner_record import EnvironmentOwnerRecord
from journal.features.team.team_part import TeamPart
from journal.features.team.team_nudges import TeamNudges


class TeamFeature(Feature[TeamData]):
    name = TeamPart.name
    title = "Team"
    help = "A journal shared with a team through its server: joining it, inviting people, the team's devices and how the sync stands."
    commands = (TeamCommand,)
    listeners = (EnvironmentOwnerRecord, ColleagueWriteGuard)
    jobs = (TeamChatFiles,)
    seeds = (SingleTeamChat,)
    data = (TeamDataReader,)
    conduct = (TeamConduct,)

    nudges = (TeamNudges.UPGRADE_NEEDED,)
