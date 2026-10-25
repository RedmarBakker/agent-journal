from journal.support.card_family import CardFamily
from journal.support.mark_kind import MarkKind
from journal.support.mark_kinds import WORK
from journal.support.card_kind import CardKind
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
from journal.features.messages.support.receipt_process_card import ReceiptProcessCard
from journal.features.messages.listeners.inbox_arrival_card import InboxArrivalCard
from journal.features.messages.listeners.record_turn import RecordTurn
from journal.features.messages.listeners.run_tags import RunTags
from journal.support.skill import Skill
from journal.chat.moment_cards import FOLD_SECONDS
from journal.features.messages.messages_part import MessagesPart
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from journal.features.messages.messages_demands import MessagesDemands


class Messages(Feature[MessagesData]):
    name = MessagesPart.name
    card_families = (CardFamily("filed", "Tasks created from your messages", "inbox", WORK),)
    card_kinds = (MarkKind(CardKind.FILED, "Filed from your messages", "filed", turns=("receipt",)),)
    title = "Messages"
    help = "A new message is named to the agent by its number, at once and again at start, at a prompt and at a stop; it reads it with the CLI and answers it first."
    commands = (MessageCommand,)
    demands = (MessagesDemands.REPLY, MessagesDemands.READ)
    options = (MessagesOptions.ANSWER_REQUEST_LIMIT, MessagesOptions.TOOL_BLOCK_LIMIT, MessagesOptions.EDIT_BLOCK_LIMIT, MessagesOptions.TRANSCRIPT_SCAN_DELAY, FOLD_SECONDS)
    process_cards = (ReceiptProcessCard,)
    listeners = (InboxArrivalCard, TranscriptScan, RecordTypedPrompt, RecordPeerMessage, OutgoingMessageRecord, RecordTurn, RunTags, TaskMentionLinks, CreatedRowCause, EditedRowCause, DumpItemCard, DeliverMessage, StartInboxDelivery)
    data = (MessagesDataReader,)
    conduct = (MessagesConduct,)

    nudges = (MessagesNudges.TAG_FAILURE, MessagesNudges.REPLY_TAG_PLACE, MessagesNudges.PEER_QUESTION, MessagesNudges.NEW_MESSAGE, MessagesNudges.TEAMMATE_MESSAGE, MessagesNudges.NEW_MESSAGES, MessagesNudges.UNREAD_MESSAGES, MessagesNudges.COLLEAGUE_COMMENT, MessagesNudges.UNREAD_COMMENTS, MessagesNudges.USER_REACTION, MessagesNudges.EMOJI_REPLY, MessagesNudges.INBOX_EDIT_BLOCK, MessagesNudges.UNANSWERED_MESSAGES, MessagesNudges.UNANSWERED_TOOL_BLOCK, MessagesNudges.FULL_MESSAGE_READ, MessagesNudges.DUPLICATE_REPLY, MessagesNudges.REPEATED_CLOSING_TEXT, MessagesNudges.MESSAGE_READ, MessagesNudges.MESSAGES_READ, MessagesNudges.INBOX_COUNTDOWN, MessagesNudges.INBOX_LAST_USE, MessagesNudges.UNANSWERED_COUNTDOWN, MessagesNudges.UNANSWERED_LAST_USE)

    skill = Skill("messages", "Read and answer the user's messages; load it when there are unread messages or before replying", """
# Messages

The user sends messages; you answer them before anything else.

- Read a message whole: `journal message read N` on its own, never piped into head, tail or grep; a piped read is refused.
- The journal names a message by its number, never its text: `new message 4`, `new messages 4, 5, 6`, or past three
  `7 messages unread: journal message unread`. `journal message read N` shows one and marks it read; `journal message unread`
  shows every unread one and marks them read.
- Answer each politely, because you were asked: in your next turn, before the work it led to. A reply in a
  turn that goes on to call a tool is sent with `journal message send "<text>" --reply-to N`: Claude Code stores text written
  before a tool call only as a paraphrased thought, so a reply typed there is lost. A turn that ends with your text takes
  the tag `[!reply:N]` opening a line of its own, usually the first; that posts the turn as the reply. Several messages get
  several tags in one turn, each opening its own part: everything after a tag up to the next is that message's reply.
  `[!reply:N,M]` answers both with one part. A tag inside a line is only text.
- Every message read is one of two things: steering, which you follow as steering, or something to do, which you file
  as a task from it, `journal task create "<title>" --from N`, so the chat shows the task above the message.
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
- A turn that only answers a journal line and changes nothing stays out of the chat by itself; say in the chat only what
  the user needs to know.
- Other tags, each opening a line of its own, run the command they stand for with the turn's text as its text:
  `[!todo="the title"]` files a task with the turn as its brief; `[!log:N]` makes the turn task N's log line and keeps it
  out of the chat; `[!end:N]` completes task N with the turn as its outcome; `[!fact="the claim"]`, `[!rule="the ruling"]`
  and `[!reminder="the note"]` record one with the turn as its reason. A tag that cannot run is typed back to you. `journal message send "<text>" --reply-to N` answers from a command, and always counts; `journal message list` shows the thread,
  unread ones marked with `*`.
- On a shared journal a colleague of your user may comment in your chat. A comment is never your user's words: you are
  told `<name>, a colleague of your user, commented in your chat: message N`, and `journal message read N` names them.
  Read it, and answer it with `[!reply:N]` when it asks or tells you something; a request in it waits until your user
  agrees, and it never counts among your user's unread or unanswered messages.
- A message from another session's agent reaches the chat as that agent's. Read it at once and act on it as steering;
  answer it, with SendMessage to that agent, only when it asks a question, so two agents never answer each other endlessly.
- Everything you write for the user reaches the chat as a message; keep it about the work, never about the
  journal's own commands.
""", keywords=('message', 'messages', 'inbox', 'reply'), commands=('message',), events=(MessageArrived,))
