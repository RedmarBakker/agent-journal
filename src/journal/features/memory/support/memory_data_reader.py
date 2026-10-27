from datetime import datetime, timezone

from journal.features.memory.support.memory_row import MemoryRow
from journal.engine.support.lazy_facts import LazyFacts
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes
from journal.features.memory.support.row_condition import RowCondition
from journal.repositories.row_counts import RowCounts
from journal.features.memory.support.timed_reminder import TimedReminder
from journal.features.memory.support.repeating_reminder import RepeatingReminder
from journal.models.agent import Agent
from journal.repositories.memories import Memories
from journal.repositories.reminders import Reminders
from journal.repositories.rules import Rules
from journal.repositories.setting_rows import SettingRows
from journal.support.card_type import CardType
from journal.features.memory.memory_options import MemoryOptions
from journal.support.time_source import TimeSource


class MemoryDataReader:
    """Reads the memory feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields MemoryData names."""

    def __init__(self, memories: Memories, rules: Rules, reminders: Reminders, settings: SettingRows, counts: RowCounts, scope: Scope, stages: StageTimes, time_source: TimeSource) -> None:
        self.time_source, self.weighted = time_source, memories
        self.rules, self.reminders, self.settings, self.counts, self.scope, self.stages = rules, reminders, settings, counts, scope, stages

    def row(self, noun: str, memory, kind: CardType) -> MemoryRow:
        ready = bool(memory.trigger) and RowCondition.read(memory.condition).is_true(self.counts)
        return MemoryRow(noun, memory.row_id, memory.text, tuple(memory.keywords), kind, memory.presence, memory.trigger, ready, memory.is_single_use)

    def read(self, agent: Agent) -> LazyFacts:
        facts = LazyFacts("memory", {
            "threshold_due": lambda: agent.threshold_due,
            "context_threshold": lambda: agent.context_threshold,
            "memories": self.memories,
            "triggered": lambda: tuple(self.row(noun, memory, kind) for noun, memory, kind in self.triggered_memories()),
            "rows": lambda: tuple(self.row(noun, memory, kind) for noun, memory, kind in self.keyword_memories()),
            "stale": lambda: self.stale([(noun, memory) for noun, memory, _ in facts.memories], self.settings.integer(MemoryOptions.STALENESS_LIMIT)),
            "shown_memories": self.shown_memories,
            "repeating": lambda: tuple(RepeatingReminder(r.row_id, r.text, r.every_minutes, r.every_tool_uses, r.said_at, r.said_tool_use) for r in self.reminders.repeating()),
            "timed": lambda: tuple(TimedReminder(r.row_id, r.text, r.due_at.timestamp()) for r in self.reminders.timed()),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)
        return facts

    def shown_memories(self) -> str:
        shown = self.weighted.shown()
        return "; ".join(f"{memory.id} (weight {memory.weight}): {memory.summary_line()}" for memory in shown) if shown else "you have no memories yet"

    def triggered_memories(self) -> list[tuple]:
        return [*(("rule", rule, CardType.RULES) for rule in self.rules.filled_rows("trigger")), *(("reminder", reminder, CardType.REMINDERS) for reminder in self.reminders.triggered())]

    def keyword_memories(self) -> list[tuple]:
        return [*(("rule", rule, CardType.RULES) for rule in self.rules.keyword_rows()), *(("reminder", reminder, CardType.REMINDERS) for reminder in self.reminders.keyword_rows())]

    def memories(self) -> list[tuple]:
        return [*(("rule", rule, CardType.RULES) for rule in self.rules.all()), *(("reminder", reminder, CardType.REMINDERS) for reminder in self.reminders.standing())]

    def stale(self, memories: list, days: int) -> tuple[str, ...]:
        moment = self.time_source.moment()
        ages = [(noun, memory.row_id, (moment - memory.update_time).days) for noun, memory in memories]
        return tuple(f"{noun} {row_id}, {age} days" for noun, row_id, age in ages if age >= days)
