from journal.support.card_family import CardFamily
from journal.support.mark_kind import MarkKind
from journal.support.mark_kinds import AGENT, REMINDERS
from journal.support.card_kind import CardKind
from journal.features.feature import Feature
from journal.features.memory.listeners.start_memory import StartMemory
from journal.features.memory.listeners.memory_hint_card import MemoryHintCard
from journal.features.memory.listeners.context_threshold_check import ContextThresholdCheck
from journal.features.memory.memory_conduct import MemoryConduct
from journal.features.memory.support.memory_data_reader import MemoryDataReader
from journal.features.memory.support.memory_data import MemoryData
from journal.features.memory.commands.fact_command import FactCommand
from journal.features.memory.commands.memory_skip_command import MemorySkipCommand
from journal.features.memory.commands.reminder_command import ReminderCommand
from journal.features.memory.commands.rule_command import RuleCommand
from journal.features.memory.listeners.compaction_card import CompactionCard
from journal.features.memory.listeners.memory_row_card import MemoryRowCard
from journal.features.memory.listeners.memory_strike_card import MemoryStrikeCard
from journal.features.memory.listeners.due_reminder_strike import DueReminderStrike
from journal.features.memory.listeners.single_use_memory_strike import SingleUseMemoryStrike
from journal.support.skill import Skill
from journal.features.memory.memory_part import MemoryPart
from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_options import MemoryOptions


class Memory(Feature[MemoryData]):
    name = MemoryPart.name
    card_families = (CardFamily("context", "Context", "gauge", AGENT), CardFamily("rules", "Rules", "rules", REMINDERS), CardFamily("facts", "Facts", "pins", REMINDERS), CardFamily("reminders", "Reminders", "reminders", REMINDERS),)
    card_kinds = (MarkKind(CardKind.COMPACTIONS, "Conversation compacted", "context"), MarkKind(CardKind.RULES, "Rules", "rules"), MarkKind(CardKind.FACTS, "Facts", "facts"), MarkKind(CardKind.REMINDERS, "Reminders", "reminders"), MarkKind("acknowledgements", "Acknowledged reminders", "reminders", main=False, shown=False, messages=("acknowledgement",)),)
    title = "Memory"
    help = "At 25, 50 and 80 percent of the context window, writes wait until the agent records a fact, a rule or nothing."
    conduct = (MemoryConduct,)
    listeners = (ContextThresholdCheck, MemoryHintCard, CompactionCard, MemoryRowCard, MemoryStrikeCard, StartMemory, DueReminderStrike, SingleUseMemoryStrike)
    data = (MemoryDataReader,)
    commands = (FactCommand, RuleCommand, ReminderCommand, MemorySkipCommand)

    nudges = (MemoryNudges.CONTEXT_DECISION, MemoryNudges.DECISION_EDIT_BLOCK, MemoryNudges.UNDECIDED_STOP, MemoryNudges.CHECK_STALE_MEMORY, MemoryNudges.RULE_SCOPE_QUESTION, MemoryNudges.MEMORY_READ_REQUEST, MemoryNudges.REMINDER_DUE, MemoryNudges.MEMORY_TRIGGERED)
    options = (MemoryOptions.STALENESS_LIMIT,)

    skill = Skill("memory", 'Decide what to keep from the context window: a fact, a rule or a reminder; load it at a context mark', """
# Memory

At a mark of the context window, writes wait until you decide what must be retained beyond it.

- A **fact** is true of this environment: `journal fact create "<what is true here>"`.
- A **rule** binds the whole project, written as the ruling itself: `journal rule create "Always ..." --reason "<why>"`.
  Only the user makes one; right after, read it again as a rule.
- A **reminder** is what to keep doing here: `journal reminder create "<do this>"`.
  With `--at "2026-10-24 09:30"` it is set for that moment instead: quiet until then, reported once then, and struck.
- One that no longer holds: `journal <fact|rule|reminder> strike <n>`.
- Nothing worth keeping: `journal memory skip "<why>"`.
- `--keywords a,b` on any of them: when you write or run one of those words and the row is not in your context
  window, you are instructed to read it, `journal reminder read <n>`, `journal fact read <n>` or `journal rule read <n>`; the
  read puts it in your context, and so do the session's start block and the look, until the next compaction.
- Facts, rules and reminders are handed to you at every session start.
- A moment can bring one back too: `--on task_completed` or `--on task_started`. With `--when '<condition>'` it comes
  back only if the condition holds at that moment, and with `--once` it is struck after it has come back. A condition
  is JSON: `{"count": "<table>", "where": {"<field>": <value or [values]>}, "is" | "at_least" | "at_most": <number>}`,
  several joined as `{"all": [...]}` or `{"any": [...]}`. For a reminder to release once every task is done:
  `journal reminder create "Release 4.48.0" --on task_completed --when '{"count": "tasks", "where": {"state":
  ["open", "started", "delegated"]}, "is": 0}' --once`. A field with set values, such as a task's state, refuses
  a value it never has. When its moment comes you are informed
  `reminder <n> is for this moment: journal reminder read <n>`; read it and act on it.
- Read this skill before any `journal fact`, `rule`, `reminder` or `memory` command: those commands wait until you have.
""", keywords=('fact', 'facts', 'rule', 'rules', 'reminder', 'remember', 'memory'), required_states=('at_mark',), commands=('fact', 'rule', 'reminder', 'memory'))
