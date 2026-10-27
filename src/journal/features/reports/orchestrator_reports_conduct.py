from dataclasses import replace

from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.ticked import Ticked
from journal.events.feature_data import FeatureData
from journal.features.reports.reports_nudges import ReportsNudges
from journal.features.reports.reports_options import ReportsOptions
from journal.features.reports.reports_part import ReportsPart
from journal.support.timeout import Timeout

# the span between two lines naming the same row never acted on, in minutes, chosen anew each time
REPEAT_LEAST_MINUTES = 20
REPEAT_SPREAD_MINUTES = 21


class OrchestratorReportsConduct(Conduct):
    """The reports conduct the orchestrator's mode state brings to every state above it: on the tick and at a stop, each report or document never acted on the set minutes after it was written is named in one line, again every 20 to 40 minutes, the span chosen anew from the minute and the row, until it is acted on or signed off."""

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        return self.none(*unacted_lines(event.data, event.time, settings))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.none(*unacted_lines(event.data, event.time, settings))


def unacted_lines(data: FeatureData, moment: float, settings: Settings) -> tuple[Nudge, ...]:
    minutes = settings.integer(ReportsOptions.UNACTED_MINUTES)
    if minutes <= 0:
        return ()
    return tuple(replace(ReportsNudges.UNACTED.create(row_type=row.row_type, n=row.row_id), repeat=Timeout.minutes(repeat_minutes(row.row_id, moment))) for row in data.part(ReportsPart).unacted if moment - row.written_at >= minutes * 60)


def repeat_minutes(row_id: int, moment: float) -> int:
    return REPEAT_LEAST_MINUTES + (row_id * 7 + int(moment // 60)) % REPEAT_SPREAD_MINUTES
