from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import AGENT
from journal.support.card_type import CardType
from journal.features.skills.listeners.skill_triggers import SkillTriggers
from journal.features.feature import Feature
from journal.features.skills.listeners.skill_obligation import SkillObligation
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
    listeners = (SkillObligation, SkillReadRecord, SkillLoadedCard, CompactionReset, SkillTriggers)
    data = (SkillsDataReader,)
    conduct = (SkillsConduct,)

    nudges = (SkillsNudges.SKILL_VIEWER_REQUEST, SkillsNudges.SKILL_READ_REQUEST, SkillsNudges.UNREAD_SKILL_STOP)

    skill = Skill("journal", 'The journal, its commands and when each applies; load it first in every session', """
# The journal

A line that starts with [journal] is the journal speaking, never the user: act on it as an instruction, and never
answer it in the chat.

The journal stores this project's lasting state beside the code and tells you what to do at the
moments you would otherwise get wrong. Every command is `journal <noun> <verb>`; `journal <noun> --help`
lists the verbs.

- **task**: what you are working on: `journal task start <n>` or `journal task create "<title>" --start`. Log its status with `journal task log <n> "<line>"`, finish
  with `journal task complete <n> --how "<outcome>"`.
- **plan**: ordered tasks. `journal plan start <n>` follows it: finishing a task starts the next.
- **message** and **question**: what you and the user write to each other. Answer unread messages first;
  `journal question ask "<text>" --options "a" "b"` waits for the user.
- **memory**, **rule**, **reminder**: what must be retained beyond the context window. A memory has a weight that
  every compaction lowers; at a context mark, writes wait until you weigh, add or remove one, or run
  `journal memory skip "<why>"`.
- **sequence**, **skill**: steps to follow, and these files.
- **worker**: an agent that writes for you, on one task: it clocks in, proves each point of the task's brief and
  clocks out; you check each proof with `journal worker check`, send a short one back, and take the work in with
  `journal worker merge`.
- **shell**: a long command moves to the background; read any output by its number with `journal output read <n> --tail 20` (or --grep, --summary, --all);
  `journal reader add` stores a reader that picks the lines worth seeing.
- **alias**: `journal alias add <name> "<line>" --reader <reader>` names a command line; `journal <name> [args]` runs it
  with the args at its end and watches a long run through its reader. Plugins ship aliases too; `journal alias list` names them.
- `journal environment overview` after a compaction or a takeover lists what is in progress, then runs the commands
  the setting briefing.look_commands names, each under its heading, a line not starting with journal in the project's shell: by default the started plan with its current phase,
  the task list, the unread messages, the workers, the open questions and the current task in full. `journal plan show
  current` and `journal task show current` show the started plan and the current task.
- `journal await "<what>" --output <n>` or `--until "<script>"` when you wait for something outside your control, then end
  your turn: the wait ends by itself once that is done.
- `journal search "<words>"` finds every task, plan, message, document, report and agent conversation here that contains
  all the words: search there before saying you do not know or asking the user again.
- Also: **report**, **doc**, **check**, **plugin**, **secret**, **template**, **notice**; `journal <noun> --help` lists the verbs.
- `journal stuck "<why>"` when you are stuck: the journal sends nothing until your next tool use.

A line from the journal is an instruction, never a message: act on it, and write nothing about it in the chat.
""")
