from journal.features.feature import Feature
from journal.features.profiles.listeners.count_profile_use import CountProfileUse
from journal.features.profiles.profiles_conduct import ProfilesConduct
from journal.features.profiles.support.profiles_data_reader import ProfilesDataReader
from journal.features.profiles.support.profiles_data import ProfilesData
from journal.features.profiles.profiles_nudges import ProfilesNudges
from journal.features.profiles.profiles_options import ProfilesOptions
from journal.features.profiles.profiles_part import ProfilesPart


class Profiles(Feature[ProfilesData]):
    """A researcher, a planner and a debugger are written as agent profiles for every provider, so a subagent exists for each job that only reads."""

    name = ProfilesPart.name
    title = "Agent profiles"
    options = (ProfilesOptions.CLAUDE_MODEL, ProfilesOptions.CODEX_MODEL)
    listeners = (CountProfileUse,)
    data = (ProfilesDataReader,)
    conduct = (ProfilesConduct,)
    nudges = (ProfilesNudges.WORKER_PROFILE_MISUSE,)
    help = "A researcher, a planner and a debugger are written as read-only subagent profiles for Claude and Codex."
