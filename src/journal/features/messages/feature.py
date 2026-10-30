from journal.events.blocking import Blocking
from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import WORK
from journal.support.card_type import CardType
from journal.events.rows.message_arrived import MessageArrived
from journal.features.feature import Feature
from journal.features.messages.support.messages_data_reader import MessagesDataReader
from journal.features.messages.support.messages_data import MessagesData
from journal.features.messages.messages_conduct import MessagesConduct
from journal.features.messages.listeners.record_typed_prompt import RecordTypedPrompt
from journal.features.messages.listeners.record_peer_message import RecordPeerMessage
from journal.features.messages.listeners.outgoing_message_record import OutgoingMessageRecord
from journal.features.messages.listeners.transcript_scan import TranscriptScan
from journal.features.messages.commands.message_command import MessageCommand
from journal.features.messages.listeners.deliver_message import DeliverMessage
from journal.features.messages.listeners.start_inbox_delivery import StartInboxDelivery
from journal.features.messages.listeners.task_mention_links import TaskMentionLinks
from journal.features.messages.listeners.created_row_cause import CreatedRowCause
from journal.features.messages.listeners.edited_row_cause import EditedRowCause
from journal.features.messages.listeners.dump_item_card import DumpItemCard
from journal.features.messages.listeners.receipt_link_removal import ReceiptLinkRemoval
from journal.features.messages.support.receipt_process_card import ReceiptProcessCard
from journal.features.messages.listeners.inbox_arrival_card import InboxArrivalCard
from journal.features.messages.listeners.record_turn import RecordTurn
from journal.support.skill import Skill
from journal.features.messages.messages_part import MessagesPart
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from journal.features.messages.messages_demands import MessagesDemands
from journal.features.messages.listeners.unlinked_number_record import UnlinkedNumberRecord


class Messages(Feature[MessagesData]):
    name = MessagesPart.name
    card_families = (CardFamily("filed", "Tasks created from your messages", "inbox", WORK),)
    card_types = (CardTypeEntry(CardType.FILED, "Filed from your messages", "filed", turns=("receipt",)),)
    title = "Messages"
    help = "A new message is named to the agent by its number, at once and again at start, at a prompt and at a stop; it reads it with the CLI and answers it first."
    commands = (MessageCommand,)
    demands = (MessagesDemands.REPLY, MessagesDemands.READ)
    options = (MessagesOptions.ANSWER_REQUEST_LIMIT, MessagesOptions.TOOL_BLOCK_LIMIT, MessagesOptions.EDIT_BLOCK_LIMIT, MessagesOptions.TRANSCRIPT_SCAN_DELAY)
    process_cards = (ReceiptProcessCard,)
    answer_listeners = ((RecordTurn, Blocking.NEXT_DECISION), (StartInboxDelivery, Blocking.ANSWER), (CreatedRowCause, Blocking.NEXT_DECISION))
    listeners = (UnlinkedNumberRecord, InboxArrivalCard, TranscriptScan, RecordTypedPrompt, RecordPeerMessage, OutgoingMessageRecord, TaskMentionLinks, EditedRowCause, DumpItemCard, ReceiptLinkRemoval, DeliverMessage)
    data = (MessagesDataReader,)
    conduct = (MessagesConduct,)

    nudges = (MessagesNudges.RETIRED_TAGS, MessagesNudges.UNLINKED_NUMBERS, MessagesNudges.MISSING_ROWS, MessagesNudges.PEER_QUESTION, MessagesNudges.NEW_MESSAGE, MessagesNudges.NEW_MESSAGES, MessagesNudges.UNREAD_MESSAGES, MessagesNudges.USER_REACTION, MessagesNudges.EMOJI_REPLY, MessagesNudges.INBOX_EDIT_BLOCK, MessagesNudges.UNANSWERED_MESSAGES, MessagesNudges.UNANSWERED_TOOL_BLOCK, MessagesNudges.FULL_MESSAGE_READ, MessagesNudges.REPLY_REPEAT_WARNING, MessagesNudges.REPLY_CLOSING_WORDS, MessagesNudges.MESSAGE_READ, MessagesNudges.REPLY_COMMAND, MessagesNudges.COMMENT_READ, MessagesNudges.INBOX_COUNTDOWN, MessagesNudges.INBOX_LAST_USE, MessagesNudges.UNANSWERED_COUNTDOWN, MessagesNudges.UNANSWERED_LAST_USE)

    skill = Skill("messages", "Read and answer the user's messages; load it when there are unread messages or before replying", """
# Messages

The user sends messages; you answer them before anything else.

- Read a message whole: `journal message read N` on its own, never piped into head, tail or grep; a piped read is refused.
- The journal names a message by its number, never its text: `new message 4`, `new messages 4, 5, 6`, or past three
  `7 messages unread: journal message unread`. `journal message read N` shows one and marks it read; `journal message unread`
  shows every unread one and marks them read.
- Answer each politely, because you were asked: at once, before the work it led to, always with
  `journal message send '<text>' --reply-to N`, single-quoted, then go on with the work in the same turn. A reply written
  as your turn's closing text ends the turn, so the work you meant to do next never happens. Words written after a reply
  in the same turn are not sent to the chat, and you are told so at the stop: end such a turn with the reply.
- Every message read is one of two things: steering, which you follow as steering, or something to do, which you file
  as a task from it, `journal task create "<title>" --from N`, so the chat shows the task above the message. A comment on
  a document or report is neither: answer it, and write what it asks into that document or report, as a change, a section
  or an open question; it becomes work only when the user asks for it.
- A number that names a row is written with its kind, task 3399 or plan 1032, so the chat links it. A message of
  yours that has one without it is pointed out to you once: fix it with `journal message amend-links <n> <kind>
  [<kind>...]`, the kinds in the order the numbers appear, or one kind for all.
- A message that only needs acknowledging ("ok", "thanks", "continue") gets a reaction, not words: `journal message react N "👍"`,
  🙏 for thanks; the same reaction again takes it off. The user's reaction to a message is acted on when it asks for something and
  never mentioned. A turn of yours that is only a reaction is not posted.
- An unread inbox is named again every third tool use; after five reminders the next write waits until you read it. A message
  you read and leave unanswered holds your very next tool call that is not a journal command or a look at its files: a word
  first, then the work. A reaction to a message answers it too.
  `read due, message N: K` and `reply due, message N: K` count the tool uses K left before that wait.
- After a compaction, a new start or a takeover, `journal environment overview` shows what is in flight, the latest
  messages among it, and must be run before any other write; `journal message recent` shows the latest messages alone.
- A picture in a message is named once you have looked: `journal message tag <n> <file> "<what it shows>"`.
- When the user must open a web address outside the journal, or send a form to one, put a button under your message
  instead of asking them to visit it: `--button 'Open the setup page|http://localhost:8765/|opens the page in a new tab'`
  opens it, and `--form-button 'Create the app|<address>|sends the manifest to GitHub|manifest=<json>'` posts the hidden
  fields to it, as GitHub's app manifest flow takes one. The label says what happens, the third part a line on it. Never
  a button for a journal row: task 12 or plan 3 written in the text is a link already.
- A turn that only answers a journal line and changes nothing stays out of the chat by itself; say in the chat only what
  the user needs to know.
- `journal message list` shows the thread, unread ones marked with `*`.
- A message from another session's agent reaches the chat as that agent's. Read it at once and act on it as steering;
  answer it, with SendMessage to that agent, only when it asks a question, so two agents never answer each other endlessly.
- Everything you write for the user reaches the chat as a message; keep it about the work, never about the
  journal's own commands.
""", keywords=('message', 'messages', 'inbox', 'reply'), commands=('message',), events=(MessageArrived,))
