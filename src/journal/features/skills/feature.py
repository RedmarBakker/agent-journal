from journal.events.blocking import Blocking
from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import AGENT
from journal.support.card_type import CardType
from journal.features.skills.listeners.skill_triggers import SkillTriggers
from journal.features.feature import Feature
from journal.features.skills.listeners.skill_obligation import SkillObligation
from journal.features.skills.listeners.message_skill_obligation import MessageSkillObligation
from journal.features.skills.skills_conduct import SkillsConduct
from journal.features.skills.support.skills_data_reader import SkillsDataReader
from journal.features.skills.support.skills_data import SkillsData
from journal.support.skill import Skill
from journal.features.skills.commands.skill_command import SkillCommand
from journal.features.skills.listeners.compaction_reset import CompactionReset
from journal.features.skills.listeners.skill_loaded_card import SkillLoadedCard
from journal.features.skills.listeners.skill_read_record import SkillReadRecord
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.skills.skills_options import SkillsOptions
from journal.features.skills.skills_part import SkillsPart


class Skills(Feature[SkillsData]):
    """Writes every feature's skill for the agent and makes it read the right one at the right moment."""

    options = (SkillsOptions.START_SKILLS, SkillsOptions.COMPACTION_SKILLS)
    name = SkillsPart.name
    card_families = (CardFamily("skills", "Skills", "book", AGENT),)
    card_types = (CardTypeEntry(CardType.SKILLS, "Skills the agent loads", "skills"),)
    title = "Skills"
    help = "The journal's skills are written for the agent and required by the states at the moments they matter: the journal's at a start, a state's at a start in it, the ones a prompt names; a write waits until the file is read."
    commands = (SkillCommand,)
    answer_listeners = ((SkillObligation, Blocking.NEXT_DECISION), (MessageSkillObligation, Blocking.NEXT_DECISION), (SkillReadRecord, Blocking.ANSWER), (CompactionReset, Blocking.NEXT_DECISION))
    listeners = (SkillLoadedCard, SkillTriggers)
    data = (SkillsDataReader,)
    conduct = (SkillsConduct,)

    nudges = (SkillsNudges.SKILL_VIEWER_REQUEST, SkillsNudges.SKILL_READ_REQUEST, SkillsNudges.UNREAD_SKILL_STOP)

    skill = Skill("journal", 'Find your way in the journal: what it is, its basic ideas and which skill to read for what; read at the start of every session, with the etiquette skill', """
# The journal

The journal keeps this project's lasting state beside the code and tells you what to do at the moments you would
otherwise get wrong.

A line that starts with [journal] is the journal speaking, never the user: act on it as an instruction, and never
answer it, quote it or write about it in the chat.

Every command is `journal <noun> <verb>`; `journal <noun> --help` lists the verbs. A row has a kind and a number,
task 12, plan 3, message 7: write both, so the chat links it.

- An environment is one line of work in this project, with its own agents, tasks and chat.
- You are an agent with a stack of states: what you do now sits over what you were doing, and gives way back to it.
- A task is the work in hand and a plan orders tasks; a message or a question is what you and the user say to each other.
- A memory keeps what matters past the context window; a worker writes for you on one task, a subagent only reads.
- A sequence is steps followed one at a time; an output is a command's output, kept and read by its number.

When the journal holds you, its line says why and names the way out. After a compaction or a new start, run
`journal environment overview` before anything else. Search before you say you do not know or ask the user again:
`journal search "<words>"`. A pin is a note the user sees on coming back, a button an action for now under your
message: the pinned-links and messages skills say which to use.

| Read | For | The journal asks for it |
|---|---|---|
| etiquette, messages | the chat, messages, questions, pins and buttons | at every start; a message, a question |
| tasks, plans | work in hand, blocks, waits, being stuck; ordered tasks | a task or plan command, a plan you follow |
| workers | workers and subagents | a worker command |
| shell, memory | commands, outputs, readers, aliases; memories, rules, reminders | an output or alias; a context mark |
| sequences, docs, reports, templates | steps; lasting knowledge; what was checked; templates | their commands |
| checks, dumps, collections, flowcharts | checks; dropped material; groups of rows; flowcharts | their commands, a check failing, a dump |
| pinned-links, plugins, secrets | links for the user; plugins; keys and logins | their commands and words |
| organization-seat-routing | route work between organization seats | a seat receives or hands off work |
""")
