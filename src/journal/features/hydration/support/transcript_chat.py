from collections import Counter
from datetime import datetime, timezone

from journal.features.hydration.support.chat_row import ChatRow
from journal.models.author import Author
from journal.models.message import Message
from journal.providers.support.turn import Turn


class TranscriptChat:
    """The chat a transcript reads as: each prompt the person typed and each reply the agent wrote, with their times, the tool calls between two of them folded into one line that counts them by tool, and the agent's thinking, the journal's injected lines and the summaries left out."""

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
        if turn.kind == "human" and turn.text.strip():
            self.append_row(Message(author=Author.USER, text=turn.text.strip(), read_at=datetime.fromtimestamp(turn.time, timezone.utc)), turn.time)
        elif turn.kind == "agent" and turn.text.strip():
            self.append_row(Message(author=Author.AGENT, session=self.session, text=turn.text.strip()), turn.time)
        self.count_tools(turn)

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
        self.rows.append(ChatRow(Message(author=Author.SYSTEM, session=self.session, text=line, data={"kind": Message.TOOL_SUMMARY}), self.tools_at))
        self.tools = Counter()
