import re
from collections import Counter
from datetime import datetime, timezone

from journal.features.hydration.support.chat_row import ChatRow
from journal.models.author import Author
from journal.models.message import Message
from journal.providers.support.turn import Turn
from journal.support.prompt_origin import PromptOrigin

MARKER_START = "[!"
REPLY_TAG = re.compile(r"^\[!reply:[^\]]*\]\s*")


class TranscriptChat:
    """The chat a transcript reads as: each prompt the person typed and each reply the agent wrote, with their times, the tool calls between two of them folded into one line that counts them by tool, and the agent's thinking, the journal's and the program's injected lines, the notices, the agent's marker lines and the summaries left out; a reply tag is taken off its reply."""

    def __init__(self, session: str) -> None:
        self.session = session
        self.rows: list[ChatRow] = []
        self.tools: Counter[str] = Counter()
        self.tools_at = 0.0

    def read(self, turns: list[Turn]) -> list[ChatRow]:
        for turn in turns:
            self.add(turn)
        self.fold_tools()
        return self.rows

    def add(self, turn: Turn) -> None:
        text = turn.text.strip()
        if turn.kind == "human" and text and PromptOrigin.is_users(text):
            self.append_row(Message(author=Author.USER, text=text, read_at=datetime.fromtimestamp(turn.time, timezone.utc)), turn.time)
        elif turn.kind == "agent" and (reply_text := self.chat_text(text)):
            self.append_row(Message(author=Author.AGENT, session=self.session, text=reply_text), turn.time)
        self.count_tools(turn)

    @staticmethod
    def chat_text(text: str) -> str:
        lines = [REPLY_TAG.sub("", line) for line in text.splitlines() if REPLY_TAG.match(line) or not line.startswith(MARKER_START)]
        return "\n".join(lines).strip()

    def append_row(self, message: Message, time: float) -> None:
        self.fold_tools()
        self.rows.append(ChatRow(message, time))

    def count_tools(self, turn: Turn) -> None:
        if turn.tools and not self.tools:
            self.tools_at = turn.time
        self.tools.update(turn.tools)

    def fold_tools(self) -> None:
        if not self.tools:
            return
        line = "Tool calls: " + ", ".join(f"{name} {count}" for name, count in self.tools.most_common())
        self.rows.append(ChatRow(Message.tool_summary(self.session, line), self.tools_at))
        self.tools = Counter()
