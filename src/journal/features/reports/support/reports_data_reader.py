from datetime import datetime, timezone

from journal.engine.support.lazy_facts import LazyFacts
from journal.features.reports.reports_nudges import ReportsNudges
from journal.features.reports.support.unacted_rows import UnactedRows
from journal.models.agent import Agent
from journal.repositories.entries import Entries
from journal.repositories.messages import Messages
from journal.repositories.reports import Reports
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes


class ReportsDataReader:
    """Reads the reports feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields ReportsData names."""

    def __init__(self, reports: Reports, entries: Entries, messages: Messages, unacted: UnactedRows, scope: Scope, stages: StageTimes) -> None:
        self.reports, self.entries, self.messages, self.unacted, self.scope, self.stages = reports, entries, messages, unacted, scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        facts = LazyFacts("reports", {
            "latest": lambda: self.reports.latest_update(),
            "unread_update": lambda: bool(facts.latest) and facts.latest[0].read_at is None,
            "offered_at": lambda: self.entries.last_lines(agent.session, ReportsNudges.UPDATE_SUGGESTION.key),
            "clock_start_at": lambda: self.clock_start(facts.latest, facts.offered_at),
            "unacted": lambda: self.unacted.rows(),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)
        return facts

    def clock_start(self, latest: list, offered_at: float) -> float:
        update_end_at = latest[0].end_at.timestamp() if latest and latest[0].end_at else 0.0
        first = self.messages.earliest_commit(datetime.fromtimestamp(max(offered_at, update_end_at), timezone.utc))
        return first[0].creation_time.timestamp() if first else 0.0
