from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import AGENT, REMINDERS
from journal.support.card_type import CardType
from journal.features.feature import Feature
from journal.features.memory.listeners.start_memory import StartMemory
from journal.features.memory.listeners.memory_hint_card import MemoryHintCard
from journal.features.memory.listeners.context_threshold_check import ContextThresholdCheck
from journal.features.memory.memory_conduct import MemoryConduct
from journal.features.memory.worker_memory_conduct import WorkerMemoryConduct
from journal.support.agent_role import AgentRole
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.features.memory.listeners.compaction_mark_clear import CompactionMarkClear
from journal.features.memory.listeners.memory_fading import MemoryFading
from journal.features.memory.listeners.memory_weigh_card import MemoryWeighCard
from journal.features.memory.listeners.memory_removal_card import MemoryRemovalCard
from journal.features.memory.listeners.repeated_reminder_record import RepeatedReminderRecord
from journal.features.memory.support.memory_data_reader import MemoryDataReader
from journal.features.memory.support.memory_data import MemoryData
from journal.features.memory.commands.memory_command import MemoryCommand
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
    card_families = (CardFamily("context", "Context", "gauge", AGENT), CardFamily("rules", "Rules", "rules", REMINDERS), CardFamily("memories", "Memories", "pins", REMINDERS), CardFamily("reminders", "Reminders", "reminders", REMINDERS),)
    card_types = (CardTypeEntry(CardType.COMPACTIONS, "Conversation compacted", "context"), CardTypeEntry(CardType.RULES, "Rules", "rules"), CardTypeEntry(CardType.MEMORIES, "Memories", "memories"), CardTypeEntry(CardType.REMINDERS, "Reminders", "reminders"), CardTypeEntry("acknowledgements", "Acknowledged reminders", "reminders", main=False, messages=("acknowledgement",)),)
    title = "Memory"
    help = "At 50, 80 and 90 percent of the context window, the agent weighs its memories: writes wait until it weighs, adds one or says why nothing needs keeping."
    conduct = (MemoryConduct,)
    helper_conduct = {AgentRole.WORKER: (WorkerMemoryConduct,)}
    states = (WeighingMemories,)
    listeners = (ContextThresholdCheck, CompactionMarkClear, MemoryFading, MemoryWeighCard, MemoryRemovalCard, RepeatedReminderRecord, MemoryHintCard, CompactionCard, MemoryRowCard, MemoryStrikeCard, StartMemory, DueReminderStrike, SingleUseMemoryStrike)
    helper_listeners = {AgentRole.WORKER: (ContextThresholdCheck, CompactionMarkClear, MemoryFading)}
    data = (MemoryDataReader,)
    commands = (RuleCommand, ReminderCommand, MemoryCommand)

    nudges = (MemoryNudges.CONTEXT_DECISION, MemoryNudges.DECISION_EDIT_BLOCK, MemoryNudges.UNDECIDED_STOP, MemoryNudges.CHECK_STALE_MEMORY, MemoryNudges.RULE_SCOPE_QUESTION, MemoryNudges.MEMORY_READ_REQUEST, MemoryNudges.REMINDER_DUE, MemoryNudges.REMINDER_REPEATED, MemoryNudges.MEMORY_TRIGGERED, MemoryNudges.WORKER_MEMORIES)
    options = (MemoryOptions.STALENESS_LIMIT,)

    skill = Skill("memory", 'Keep what matters beyond the context window: memories with a weight, rules and reminders; load it at a context mark', """
# Memory

What you keep in mind lasts only as long as you keep judging it worth keeping.

- A **memory** is what to keep in mind here, in one or two plain sentences, with a weight from 1 to 10:
  `journal memory add "<what to keep in mind>" --weight 7`. Every compaction lowers every weight by one, and at
  nought the memory is no longer shown.
- `journal memory weigh 3,7,9 5,8,2` gives each memory its own weight, in order; `journal memory weigh 3,7,9 5` gives
  them all one. Raising a memory after a compaction keeps it where it was.
- `journal memory list` names every memory with its number and weight, heaviest first; `journal memory remove 3,7`
  takes out the ones that are no longer true.
- At 50, 80 and 90 percent of the context window you weigh your memories: writes and stops wait until you weigh,
  add or remove one, or say why nothing needs keeping with `journal memory skip "<why>"`. Reads and journal commands
  go through.
- After a compaction the overview opens with your memories by weight: weigh them right after it.
- A **rule** binds the whole project, written as the ruling itself: `journal rule create "Always ..." --reason "<why>"`.
  Only the user makes one; right after, read it again as a rule.
- A **reminder** is what to keep doing here: `journal reminder create "<do this>"`.
  With `--at "2026-10-24 09:30"` it is set for that moment instead: quiet until then, reported once then, and struck.
- A rule or reminder that no longer holds: `journal <rule|reminder> strike <n>`.
- `--keywords a,b` on a rule or reminder: when you write or run one of those words and the row is not in your
  context window, you are told to read it, `journal reminder read <n>` or `journal rule read <n>`.
- A moment can bring a rule or reminder back too: `--on task_completed` or `--on task_started`. With
  `--when '<condition>'` it comes back only if the condition holds at that moment, and with `--once` it is struck
  after it has come back. A condition is JSON: `{"count": "<table>", "where": {"<field>": <value or [values]>},
  "is" | "at_least" | "at_most": <number>}`, several joined as `{"all": [...]}` or `{"any": [...]}`.
- Read this skill before any `journal memory`, `rule` or `reminder` command: those commands wait until you have.
""", keywords=('memory', 'memories', 'remember', 'rule', 'rules', 'reminder'), required_states=('weighing_memories',), commands=('memory', 'rule', 'reminder'))
