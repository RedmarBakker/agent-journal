from datetime import datetime, timezone

from journal.features.memory.support.memory_row import MemoryRow
from journal.features.memory.support.memory_data import MemoryData
from journal.features.memory.support.row_condition import RowCondition
from journal.repositories.row_counts import RowCounts
from journal.features.memory.support.timed_reminder import TimedReminder
from journal.models.agent import Agent
from journal.repositories.facts import Facts
from journal.repositories.reminders import Reminders
from journal.repositories.rules import Rules
from journal.repositories.setting_rows import SettingRows
from journal.support.card_kind import CardKind
from journal.features.memory.memory_options import MemoryOptions


class MemoryDataReader:
    """Reads the memory feature's part of the feature data for an agent."""

    def __init__(self, facts: Facts, rules: Rules, reminders: Reminders, settings: SettingRows, counts: RowCounts) -> None:
        self.facts, self.rules, self.reminders, self.settings, self.counts = facts, rules, reminders, settings, counts

    def row(self, noun: str, memory, kind: CardKind) -> MemoryRow:
        ready = bool(memory.trigger) and RowCondition.read(memory.condition).is_true(self.counts)
        return MemoryRow(noun, memory.row_id, memory.text, tuple(memory.keywords), kind, memory.presence, memory.trigger, ready, memory.is_single_use)

    def read(self, agent: Agent) -> MemoryData:
        rows = [*(self.row("fact", fact, CardKind.FACTS) for fact in self.facts.scoped()), *(self.row("rule", rule, CardKind.RULES) for rule in self.rules.all()), *(self.row("reminder", reminder, CardKind.REMINDERS) for reminder in self.reminders.standing())]
        return MemoryData(threshold_due=agent.threshold_due, context_threshold=agent.context_threshold, rows=tuple(rows), stale=self.stale(self.settings.integer(MemoryOptions.STALENESS_LIMIT)), timed=tuple(TimedReminder(r.row_id, r.text, r.due_at.timestamp()) for r in self.reminders.timed()))

    def stale(self, days: int) -> tuple[str, ...]:
        moment = datetime.now(timezone.utc)
        aged = [("fact", row) for row in self.facts.scoped()] + [("rule", row) for row in self.rules.all()] + [("reminder", row) for row in self.reminders.standing()]
        ages = [(kind, row.row_id, (moment - row.update_time).days) for kind, row in aged]
        return tuple(f"{kind} {row_id}, {age} days" for kind, row_id, age in ages if age >= days)
