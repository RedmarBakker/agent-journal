from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent.ticked import Ticked
from journal.features.briefing.support.briefing_data import BriefingData
from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.briefing.briefing_part import BriefingPart
from journal.features.briefing.states.reading_overview import ReadingOverview

COMPACT = "compact"


class BriefingConduct(Conduct):
    """The briefing feature's conduct in every state: the start block at every session start but a resume, whose conversation already holds it, ready, quiet, the laws, a takeover, the rules, facts and reminders and what waits, then the overview required before the first write, and after a compaction the push of ReadingOverview, which lets nothing but the overview and the pending skills through until it has run; a write and a stop blocked until the agent has looked at what is in flight."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        if event.is_resume():
            return self.none()
        lines = [*start_block(event.data.part(BriefingPart), event.source), *folder_check(event)]
        if event.is_compaction_start():
            return self.push(ReadingOverview(), *lines, BriefingNudges.OVERVIEW_FIRST.create())
        return self.none(*lines, BriefingNudges.OVERVIEW_REQUEST.create())

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if event.subagent or not event.call.writes or event.data.part(BriefingPart).is_overview_read:
            return self.none()
        return self.refuse(BriefingNudges.OVERVIEW_REQUEST.create())

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        briefing = event.data.part(BriefingPart)
        if not briefing.is_launch_folder_missing:
            return self.none()
        return self.none(BriefingNudges.FOLDER_MISSING.create(env=briefing.environment, launch_folder=briefing.launch_folder))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.none() if event.data.part(BriefingPart).is_overview_read else self.refuse(BriefingNudges.OVERVIEW_STOP.create())



# a session started in another folder than its launch named works in one checkout while the journal looks at another
def folder_check(event: SessionStarted) -> list[Nudge]:
    briefing = event.data.part(BriefingPart)
    if not event.folder or not briefing.launch_folder or event.folder.rstrip("/") == briefing.launch_folder.rstrip("/"):
        return []
    return [BriefingNudges.FOLDER_MISMATCH.create(folder=event.folder, env=briefing.environment, launch_folder=briefing.launch_folder)]


def start_block(briefing: BriefingData, source: str) -> list[Nudge]:
    takeover_at = "" if source == COMPACT else briefing.peer_session_active_at
    optional = (
        (takeover_at, lambda: BriefingNudges.TAKEOVER.create(time=takeover_at)),
        (source != COMPACT and briefing.team_history, lambda: BriefingNudges.TEAM_HISTORY.create(rows=briefing.team_history)),
        (briefing.rules, lambda: BriefingNudges.ACTIVE_RULES.create(count=briefing.rules_count, rows=briefing.rules)),
        (briefing.facts, lambda: BriefingNudges.ENVIRONMENT_FACTS.create(rows=briefing.facts)),
        (briefing.reminders, lambda: BriefingNudges.ENVIRONMENT_REMINDERS.create(rows=briefing.reminders)),
        (briefing.interrupted_runs, lambda: BriefingNudges.INTERRUPTED_RUNS.create(rows=briefing.interrupted_runs)),
        (briefing.waiting, lambda: BriefingNudges.PENDING_ITEMS.create(rows=briefing.waiting)),
    )
    return [BriefingNudges.JOURNAL_READY.create(env=briefing.environment), BriefingNudges.JOURNAL_DISCRETION.create(), BriefingNudges.JOURNAL_LAWS.create(), *(line() for matched, line in optional if matched)]
