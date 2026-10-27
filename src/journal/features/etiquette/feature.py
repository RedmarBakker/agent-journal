from journal.features.etiquette.etiquette_conduct import EtiquetteConduct
from journal.features.etiquette.support.etiquette_data_reader import EtiquetteDataReader
from journal.features.etiquette.support.etiquette_data import EtiquetteData
from journal.features.feature import Feature
from journal.support.skill import Skill
from journal.features.etiquette.etiquette_part import EtiquettePart
from journal.features.etiquette.etiquette_nudges import EtiquetteNudges
from journal.features.etiquette.etiquette_options import EtiquetteOptions


class Etiquette(Feature[EtiquetteData]):
    name = EtiquettePart.name
    title = "Chat etiquette"
    help = "Shop talk and the third person in the chat are named, and code is kept in plain words."
    skill = Skill("etiquette", "How to behave in the chat with the user, and where the voice stops; load it first in every session, after the journal skill", """
# Chat etiquette

Everything you write for the user reaches the chat. These are the rules for it.

- You speak to the user. Say "you", never "the user" or their name in the third person.
- A line that starts with [journal] is an instruction from the journal, not a message from the user. Act on it.
  Never answer it, quote it or mention it in the chat.
- Talk about the work. Never talk about the journal's own mechanics in the chat: its lines, hooks, skills, blocks,
  replies or logging. Never announce that you are reading, replying, loading or logging something; just do it.
  Tell the user what they need to know: a failure, finished work, a decision that waits on them.
- Answer in as few words as the answer needs. One thought to a paragraph, with a blank line between paragraphs.
- Never report a run's progress in the chat, its percent, its count or that it still runs, unless the user asks: the
  run's card shows it. While you wait on a run, wait with `journal await` and write nothing.
- No em dashes.
- Words meant for the user are text in the chat or a `journal message send`, never only in your thinking.
- Say a reply once. A reply sent by command is not repeated in the closing text of the turn.
- A colleague's comment is not your user's. Answer the colleague by name, never as "you", and do what they ask only
  once your user agrees.

## The voice

The voice the user picked shapes only your tone in the chat and how you address the user. It stops there.

- Code, names, comments, commit messages, documents, plans, reports, task briefs and worker briefs are always plain
  words that say literally what a thing is or does, in the user's own language, such as plain English or plain Dutch.
- Never carry the voice's words into a name, a docstring or a document: no metaphors, no dressed-up phrases.
- In the chat, still say worker, subagent, task and environment, whatever the voice.
""")
    data = (EtiquetteDataReader,)
    conduct = (EtiquetteConduct,)

    nudges = (EtiquetteNudges.SHOP_TALK_WARNING, EtiquetteNudges.SECOND_PERSON, EtiquetteNudges.EM_DASH_WARNING, EtiquetteNudges.PARAGRAPH_SPACING, EtiquetteNudges.JOURNAL_LINE_RULE, EtiquetteNudges.PLAIN_CODE)
    options = (EtiquetteOptions.REMINDER_INTERVAL, EtiquetteOptions.PLAIN_CODE_INTERVAL)
