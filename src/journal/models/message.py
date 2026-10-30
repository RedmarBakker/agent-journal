from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from journal.events.rows.message_arrived import MessageArrived
from journal.events.rows.message_read import MessageRead
from journal.events.rows.reply_posted import ReplyPosted
from journal.support.message_thread import MessageThread
from journal.models.author import Author
from journal.models.scoped import Scoped
from journal.models.support.commentable import Commentable
from journal.models.support.message_button import MessageButton
TERMINAL_LINE = "typed"


@dataclass(frozen=True)
class Message(Scoped, Commentable):
    """A bubble of a chat: who wrote it, its words and files, and the session and kind of the agent whose chat it is in."""

    text_fields: ClassVar[tuple[str, ...]] = ("text",)

    THOUGHT = "thought"
    SCHEDULED_PROMPT = "scheduled prompt"
    REPORT = "report"
    PEER = "peer"
    RECIPIENT_KEY = "sent_to"
    ASKS_KEY = "asks"
    HYDRATION = "hydration"
    TOOL_SUMMARY = "tool_summary"
    MISSING_ROWS = "missing_rows"

    author: Author = Author.USER
    session: str | None = None
    thread: MessageThread = MessageThread.MAIN
    text: str = ""
    reply_target: int | None = None
    read_at: datetime | None = None
    read_position: int = 0
    idempotency: str = ""
    acknowledgement: bool = False
    files: tuple[str, ...] = ()
    captions: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)

    @classmethod
    def agent_message(cls, sender: str, text: str, session: str, time: datetime, asks: bool) -> "Message":
        return cls(author=Author.SYSTEM, text=text, read_at=time, session=session, data={"kind": cls.PEER, cls.PEER: sender, cls.ASKS_KEY: asks})

    @classmethod
    def agent_word(cls, sender: str, text: str) -> "Message":
        return cls(author=Author.SYSTEM, text=text, data={"kind": cls.PEER, cls.PEER: sender, cls.ASKS_KEY: False})

    @classmethod
    def outgoing(cls, receiver: str, text: str, session: str, address: str = "") -> "Message":
        return cls(author=Author.SYSTEM, text=text, session=session, data={"kind": cls.PEER, cls.RECIPIENT_KEY: receiver, "address": address or receiver})

    @classmethod
    def send_failed(cls, receiver: str, text: str, session: str, address: str, reason: str) -> "Message":
        return cls(author=Author.SYSTEM, text=text, session=session, data={"kind": cls.PEER, cls.RECIPIENT_KEY: receiver, "address": address or receiver, "failure": reason})

    @classmethod
    def flowchart(cls, title: str, edges: list[list[str]]) -> "Message":
        return cls(author=Author.SYSTEM, text=title, data={"kind": "flowchart", "edges": edges})

    @classmethod
    def tool_summary(cls, session: str, text: str) -> "Message":
        return cls(author=Author.SYSTEM, session=session, text=text, data={"kind": cls.TOOL_SUMMARY})

    @classmethod
    def hydration(cls, provider: str, session: str, text: str) -> "Message":
        return cls(author=Author.SYSTEM, text=text, data={"kind": cls.HYDRATION, "provider": provider, "session": session, "reading_request": False})

    def with_buttons(self, buttons: list[MessageButton]) -> "Message":
        return self.with_merged("data", {"buttons": [button.stored() for button in buttons]}) if buttons else self

    def with_reading_request(self) -> "Message":
        return self.with_merged("data", {"reading_request": True})

    def user_text(self) -> str:
        return self.text_body if self.is_user_message() else ""

    def with_read_time(self, read_at: datetime, tool_use: int, commented_writing: str | None) -> "Message":
        return self.with_(read_at=read_at, read_position=tool_use).with_event(MessageRead(environment_id=self.environment_id, time=read_at.timestamp(), row_id=self.id, user_text=self.user_text(), commented_writing=commented_writing))

    @classmethod
    def answer(cls, target: "Message", text: str) -> "Message":
        reply_event = ReplyPosted(reply_target=target.id)
        if target.is_main_thread():
            return cls(author=Author.AGENT, text=text, reply_target=target.id).with_event(reply_event)
        return cls(author=Author.AGENT, text=text, reply_target=target.id, session=target.session, thread=target.thread).with_event(reply_event)

    def authored(self, session: str | None) -> "Message":
        return self.with_(session=session) if self.is_new and self.session is None and self.is_main_thread() else self

    def arrived(self) -> "Message":
        return self.with_event(MessageArrived(text=self.text))

    @property
    def sender(self) -> str:
        return self.data[self.PEER] if self.PEER in self.data else f"the {self.author}"

    @property
    def is_agents_reply(self) -> bool:
        return self.reply_target is not None and self.is_agent_message()

    @property
    def quoted_lines(self) -> int:
        lines = self.text.split("\n")
        return next((i for i, line in enumerate(lines) if not line.startswith(">")), len(lines))

    @property
    def is_passage_comment(self) -> bool:
        return self.quoted_lines > 0 and self.reply_target is None

    @property
    def quote(self) -> str:
        return "\n".join(line.removeprefix(">").strip() for line in self.text.split("\n")[: self.quoted_lines])

    @property
    def text_body(self) -> str:
        return "\n".join(self.text.split("\n")[self.quoted_lines:]).strip()

    def scheduled(self) -> "Message":
        return self.with_(author=Author.SYSTEM, data={**self.data, "kind": self.SCHEDULED_PROMPT})

    @property
    def is_scheduled_prompt(self) -> bool:
        return self.data.get("kind") == self.SCHEDULED_PROMPT

    @property
    def is_thought(self) -> bool:
        return self.data.get("kind") == self.THOUGHT

    @property
    def is_terminal_line(self) -> bool:
        return self.data.get("kind") == TERMINAL_LINE

    @property
    def is_main_unread(self) -> bool:
        return (self.is_user_message() or self.is_agent_word) and self.read_at is None and self.is_main_thread()

    @property
    def is_agent_word(self) -> bool:
        return self.PEER in self.data

    @property
    def is_user_facing(self) -> bool:
        return self.is_agent_message() and not self.acknowledgement and not self.is_thought

    def is_agent_message(self) -> bool:
        return self.author == Author.AGENT

    def is_user_message(self) -> bool:
        return self.author == Author.USER

    def is_main_thread(self) -> bool:
        return self.thread == MessageThread.MAIN

