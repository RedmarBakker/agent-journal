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
        stored = [*(("fact", fact, CardKind.FACTS) for fact in self.facts.scoped()), *(("rule", rule, CardKind.RULES) for rule in self.rules.all()), *(("reminder", reminder, CardKind.REMINDERS) for reminder in self.reminders.standing())]
        rows = tuple(self.row(noun, memory, kind) for noun, memory, kind in stored)
        return MemoryData(threshold_due=agent.threshold_due, context_threshold=agent.context_threshold, rows=rows, stale=self.stale([(noun, memory) for noun, memory, _ in stored], self.settings.integer(MemoryOptions.STALENESS_LIMIT)), timed=tuple(TimedReminder(r.row_id, r.text, r.due_at.timestamp()) for r in self.reminders.timed()))

    @staticmethod
    def stale(memories: list, days: int) -> tuple[str, ...]:
        moment = datetime.now(timezone.utc)
        ages = [(noun, memory.row_id, (moment - memory.update_time).days) for noun, memory in memories]
        return tuple(f"{noun} {row_id}, {age} days" for noun, row_id, age in ages if age >= days)
