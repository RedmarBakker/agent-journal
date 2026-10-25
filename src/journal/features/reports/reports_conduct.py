from dataclasses import replace

from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.events.agent.stop import Stop
from journal.events.agent.ticked import Ticked
from journal.events.feature_data import FeatureData
from journal.support.timeout import Timeout
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.commit_detected import CommitDetected
from journal.features.reports.reports_nudges import ReportsNudges
from journal.features.reports.reports_options import ReportsOptions
from journal.features.reports.reports_part import ReportsPart
from journal.features.workers.workers_options import WorkersOptions
from journal.features.workers.workers_profiles import WorkersProfiles

# the span between two lines naming the same row never acted on, in minutes, chosen anew each time
REPEAT_LEAST_MINUTES = 20
REPEAT_SPREAD_MINUTES = 21



class ReportsConduct(Conduct):
    """The reports feature's conduct in every state: after a commit the agent is offered to write an update, at most once in the set minutes, counted from the first commit after the last offer or update, and never while an update the user has not read waits; and in orchestrator mode, on the tick and at a stop, each report or document never acted on the set minutes after it was written is named in one line, again every 20 to 40 minutes, the span chosen anew from the minute and the row, until it is acted on or signed off."""

    def on_commit_detected(self, event: CommitDetected, settings: Settings) -> Transition:
        data = event.data.part(ReportsPart)
        minutes = settings.integer(ReportsOptions.UPDATE_INTERVAL)
        if data.unread_update or minutes <= 0 or not data.clock_start_at or not Timeout.minutes(minutes).started(data.clock_start_at).is_elapsed(event.time):
            return self.none()
        return self.none(ReportsNudges.UPDATE_SUGGESTION.create())

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        return self.none(*unacted_lines(event.data, event.time, settings))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.none(*unacted_lines(event.data, event.time, settings))


def unacted_lines(data: FeatureData, now: float, settings: Settings) -> tuple[Nudge, ...]:
    minutes = settings.integer(ReportsOptions.UNACTED_MINUTES)
    if settings.value(WorkersOptions.MODE) != WorkersProfiles.ORCHESTRATOR.mode or minutes <= 0:
        return ()
    return tuple(replace(ReportsNudges.UNACTED.create(kind=row.kind, n=row.row_id, title=row.title), repeat=Timeout.minutes(repeat_minutes(row.row_id, now))) for row in data.part(ReportsPart).unacted if now - row.written_at >= minutes * 60)


def repeat_minutes(row_id: int, now: float) -> int:
    return REPEAT_LEAST_MINUTES + (row_id * 7 + int(now // 60)) % REPEAT_SPREAD_MINUTES
