from argparse import Namespace
from datetime import datetime, timezone

from journal.console.command import Command
from journal.support.caller import Caller
from journal.models.author import Author
from journal.models.message import Message
from journal.support.voice_key import VoiceKey
from journal.models.support.ref import Ref
from journal.config import Config
from journal.features.messages.support.flowchart_edges import FlowchartEdges
from journal.features.messages.support.message_files import MessageFiles
from journal.features.messages.support.reaction_emoji import ReactionEmoji
from journal.support.missing_row import MissingRow
from journal.repositories.entries import Entries
from journal.features.messages.support.passage_place import PassagePlace
from journal.repositories.agents import Agents
from journal.repositories.messages import Messages
from journal.repositories.links import Links
from journal.repositories.reactions import Reactions
from journal.features.messages.support.tags import Tags
from journal.features.messages.support.unlinked_row_numbers import PLAIN, ROW_TABLES, UnlinkedRowNumbers
from journal.repositories.rows import Rows
from journal.support.rejection import Rejection

REPLY_TAG_REFUSED = "a [!reply:N] tag answers in your turn's text; a message sent by command answers with --reply-to N, the tag left out"

RECENT_MESSAGES = 20
DUPLICATE_REPLY_LINE = "message {n} already has your reply {reply}: not sent. Send it again only if it says something new, with --confirm"


class MessageCommand(Command):
    noun = "message"
    uncut_verbs = frozenset({"read", "unread"})

    def __init__(self, messages: Messages, reactions: Reactions, links: Links, config: Config, agents: Agents, rows: Rows, files: MessageFiles, entries: Entries, passages: PassagePlace) -> None:
        self.agents, self.rows, self.files, self.entries, self.passages = agents, rows, files, entries, passages
        self.messages, self.reactions, self.links, self.config = messages, reactions, links, config

    def arguments(self, verbs) -> None:
        transmit = self.verb(verbs, "send", "leave a message")
        transmit.add_argument("text")
        transmit.add_argument("--reply-to", type=int, default=None)
        transmit.add_argument("--file", action="append", default=[], metavar="PATH", help="a file the user downloads, shown under the message, a picture inline; repeat it for more files")
        transmit.add_argument("--confirm", action="store_true", help="send a second reply to a message already answered")
        chart = self.verb(verbs, "flowchart", "draw a flowchart in the chat, which opens large in a dialog")
        chart.add_argument("title", help="what the flowchart shows, in the user's words")
        chart.add_argument("--edge", action="append", default=[], metavar="ARROW", help="one arrow, 'From -> To' or 'From -> To: label'; repeat it for each arrow, the first arrow's start being the top")
        self.verb(verbs, "list", "every message here")
        self.verb(verbs, "read", "show a message and mark it read").add_argument("n", type=int)
        self.verb(verbs, "unread", "show every unread message and mark them read")
        self.verb(verbs, "recent", "the latest messages")
        tag = self.verb(verbs, "tag", "say what an attached picture shows, so it can be found later")
        tag.add_argument("n", type=int)
        tag.add_argument("name")
        tag.add_argument("caption")
        link = self.verb(verbs, "amend-links", "write the kind before each number of your message that has none, so the chat links them: the kinds in the order the numbers appear, or one kind for all")
        link.set_defaults(verb="amend_links")
        link.add_argument("n", type=int, help="the message")
        link.add_argument("kinds", nargs="+", choices=[*sorted(ROW_TABLES), PLAIN], help="task, plan, worker, report, doc, question or message, one for each number in order, or one for all; none for a number that names no row, which stays as written")
        editing = self.verb(verbs, "edit", "write the text of your own message anew, in place, with its links and reply as they were; correct a message this way, never with a second one")
        editing.add_argument("n", type=int)
        editing.add_argument("text")
        react = self.verb(verbs, "react", "put an emoji on a message, or take it off again")
        react.add_argument("n", type=int)
        react.add_argument("emoji")

    def send(self, args: Namespace, caller: Caller) -> int:
        author = Author.build(caller.actor)
        if Tags.replies(args.text):
            raise Rejection(REPLY_TAG_REFUSED)
        files = self.files.read(args.file)
        if args.reply_to and author == Author.AGENT:
            return self.reply(self.messages.find(args.reply_to), args, caller, files)
        waiting = self.messages.unanswered() if author == Author.AGENT else []
        if len(waiting) == 1:
            return self.reply(waiting[0], args, caller, files)
        draft = Message(author=author, text=args.text, reply_target=args.reply_to, data={"kind": "plugin", "plugin": caller.plugin_name} if caller.plugin_name else {})
        message = self.files.attached(self.messages.save(draft.arrived() if author == Author.USER else draft, caller.actor), files, caller.actor)
        print(f"message {message.id} sent")
        return 0

    def flowchart(self, args: Namespace, caller: Caller) -> int:
        message = self.messages.save(Message.flowchart(args.title, FlowchartEdges.read(args.edge)), caller.actor)
        print(f"flowchart {message.id} drawn")
        return 0

    def reply(self, answered: Message, args: Namespace, caller: Caller, files: dict[str, bytes]) -> int:
        key = VoiceKey.create("reply", str(answered.row_id), args.text.strip())
        if self.messages.sent_with(key):
            print(f"message {answered.id} already has this reply in the chat: not sent again")
            return 0
        older = self.messages.first_reply(answered)
        if older is not None and not args.confirm:
            print(DUPLICATE_REPLY_LINE.format(n=answered.id, reply=older.id))
            return 1
        message = self.files.attached(self.messages.save(Message.answer(answered, args.text).with_(idempotency=key), caller.actor), files, caller.actor)
        self.messages.read(answered, caller.actor, self._tool_use(caller))
        print(f"message {message.id} sent")
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        for message in self.messages.selected(self.messages.main_chat().order("id")):
            threshold = " " if message.read_at else "*"
            print(f"{threshold}{message.id:>4}  {message.author:<5} {message.text_body}")
        return 0

    def read(self, args: Namespace, caller: Caller) -> int:
        if not self.messages.is_stored(args.n):
            return self.deleted(args.n)
        self.show(self.messages.read(self.messages.find(args.n), caller.actor, self._tool_use(caller)))
        return 0

    def deleted(self, number: int) -> int:
        deletions = self.entries.deletions(Message.table(), number)
        if not deletions:
            raise MissingRow(Message.table(), number)
        deleter = deletions[0].actor
        print(f"message {number} was deleted by {'the user' if deleter.is_user() else deleter.lookup}; nothing to do")
        return 0

    def unread(self, args: Namespace, caller: Caller) -> int:
        waiting = self.messages.unread()
        if not waiting:
            print("nothing unread")
        for message in waiting:
            self.show(self.messages.read(message, caller.actor, self._tool_use(caller)))
        return 0

    def recent(self, args: Namespace, caller: Caller) -> int:
        for message in self.messages.recent(RECENT_MESSAGES):
            print(f"{message.id:>4}  {message.author:<5} {message.text_body}")
        return 0

    def amend_links(self, args: Namespace, caller: Caller) -> int:
        message = self.messages.find(args.n)
        if message.author != Author.AGENT:
            raise Rejection(f"message {args.n} is not the agent's: only the agent's own messages are linked this way")
        spans = UnlinkedRowNumbers.spans(message.text)
        if not spans:
            raise Rejection(f"message {args.n} has no number without its kind before it")
        kinds = args.kinds * len(spans) if len(args.kinds) == 1 else args.kinds
        if len(kinds) != len(spans):
            raise Rejection(f"message {args.n}: {len(spans)} numbers lack a kind, you gave {len(args.kinds)}; one each, or one for all")
        missing = [f"{type_name} {number}" for (number, _), type_name in zip(spans, kinds) if type_name != PLAIN and not self.rows.is_row(Ref(ROW_TABLES[type_name], number))]
        if missing:
            raise Rejection(f"no {', no '.join(missing)} exists, so nothing was changed: give the kind each number really is")
        linked = self.messages.save(message.with_(text=UnlinkedRowNumbers.linked(message.text, kinds)), caller.actor)
        print(f"message {args.n} now reads: {linked.text}")
        return 0

    def edit(self, args: Namespace, caller: Caller) -> int:
        message = self.messages.find(args.n)
        if message.author != Author.AGENT:
            raise Rejection(f"message {args.n} is not the agent's: only the agent's own messages are edited")
        edited = self.messages.save(message.with_(text=args.text), caller.actor)
        print(f"message {args.n} now reads: {edited.text}")
        return 0

    def react(self, args: Namespace, caller: Caller) -> int:
        if args.emoji not in ReactionEmoji.ALL:
            print(f"a reaction is one of {' '.join(ReactionEmoji.ALL)}")
            return 1
        author = Author.build(caller.actor)
        message = self.messages.find(args.n)
        reaction = self.reactions.toggle(message, args.emoji, author, caller.actor)
        if reaction and author == Author.AGENT:
            self.messages.read(message, caller.actor, self._tool_use(caller))
        print(f"{args.emoji} {'on' if reaction else 'off'} message {args.n}")
        return 0

    def tag(self, args: Namespace, caller: Caller) -> int:
        message = self.messages.find(args.n)
        if args.name not in message.files:
            print(f"message {args.n} has no file named {args.name}")
            return 1
        self.messages.save(message.with_(captions={**message.captions, args.name: args.caption}), caller.actor)
        print(f"{args.name} on message {args.n}: {args.caption}")
        return 0

    @staticmethod
    def reply_target(message: Message) -> str:
        if message.reply_target:
            return f", a reply to message {message.reply_target}"
        return ", on the passage quoted below it" if message.quoted_lines else ""

    def show(self, message: Message) -> None:
        print(f"message {message.id} from {message.sender}{self.reply_target(message)}: {message.text_body}")
        for line in message.quote.split("\n") if message.is_passage_comment else ():
            print(f"  > {line}")
        for name in message.files:
            path = self.config.files / "message" / str(message.id) / name
            viewed = message.captions.get(name)
            print(f"  file {path}" + (f": {viewed}" if viewed else f" (open it, then `journal message tag {message.id} \"{name}\" \"<what it shows>\"`)"))
        for link in self.links.link_rows(message):
            counterpart = link.target if link.source == Ref.build(message) else link.source
            print(f"  {link.link_type} {counterpart}")
            if link.link_type == Messages.COMMENT_LINK and message.is_passage_comment:
                print(self.passages.line(counterpart, message.quote))

    def _tool_use(self, caller: Caller) -> int:
        agents = self.agents.global_matching(session=caller.session) if caller.session is not None else [agent for agent in (self.agents.current(),) if agent]
        return agents[0].tool_uses if agents else 0
