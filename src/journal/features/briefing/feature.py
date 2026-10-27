from journal.features.briefing.listeners.session_exclusivity import SessionExclusivity
from journal.features.briefing.listeners.end_silent_sessions import EndSilentSessions
from journal.features.briefing.listeners.start_overview_obligation import StartOverviewObligation
from journal.features.feature import Feature
from journal.features.briefing.briefing_conduct import BriefingConduct
from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.briefing.support.briefing_data_reader import BriefingDataReader
from journal.features.briefing.support.briefing_data import BriefingData
from journal.features.briefing.briefing_part import BriefingPart
from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.briefing.briefing_options import BriefingOptions


class Briefing(Feature[BriefingData]):
    name = BriefingPart.name
    title = "Session briefing"
    help = "Every session start, and every resume after a compaction, tells the agent where it is and what binds it: the start block, the engine's own, said before any state's own line at the start."
    conduct = (BriefingConduct,)
    states = (ReadingOverview,)
    listeners = (StartOverviewObligation, SessionExclusivity, EndSilentSessions)
    data = (BriefingDataReader,)
    options = (BriefingOptions.OVERVIEW_COMMANDS,)

    nudges = (BriefingNudges.FOLDER_MISMATCH, BriefingNudges.FOLDER_MISSING, BriefingNudges.JOURNAL_READY, BriefingNudges.JOURNAL_DISCRETION, BriefingNudges.JOURNAL_LAWS, BriefingNudges.TAKEOVER, BriefingNudges.TEAM_HISTORY, BriefingNudges.ACTIVE_RULES, BriefingNudges.ENVIRONMENT_MEMORIES, BriefingNudges.ENVIRONMENT_REMINDERS, BriefingNudges.INTERRUPTED_RUNS, BriefingNudges.PENDING_ITEMS, BriefingNudges.COMPACTION_SUMMARY, BriefingNudges.OVERVIEW_REQUEST, BriefingNudges.OVERVIEW_FIRST, BriefingNudges.OVERVIEW_STOP)
