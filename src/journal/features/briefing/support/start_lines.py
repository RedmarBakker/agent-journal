from datetime import datetime, timedelta, timezone

from journal.events.agent.session_started import SessionStarted
from journal.features.memory.support.closed_rows import ClosedRows
from journal.models.memory import Memory
from journal.models.environment import Environment
from journal.models.message import Message
from journal.repositories.agents import Agents
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.memories import Memories
from journal.repositories.messages import Messages
from journal.repositories.questions import Questions
from journal.repositories.reminders import Reminders
from journal.repositories.rules import Rules
from journal.repositories.tasks import Tasks
from journal.support.time_source import TimeSource

TAKEOVER_WINDOW = timedelta(days=1)
HISTORY_MESSAGES = 10
HISTORY_CHARACTERS = 200


INTERRUPTION_WINDOW = timedelta(minutes=30)


class StartLines:
    """What the start block names, worked out here once: when another session worked here lately, the rules and reminders numbered, the memories still shown by number and weight, heaviest first, each naming the rows its text names that have closed or gone since so the agent checks it still holds, what waits, and in the Team chat its last ten messages and answers, each cut to 200 characters, so an agent on a machine that claimed it picks up from them; the briefing conduct says the block from the feature data that carries them."""

    def __init__(self, agents: Agents, rules: Rules, memories: Memories, reminders: Reminders, tasks: Tasks, messages: Messages, questions: Questions, outputs: CommandOutputs, time_source: TimeSource, closed_rows: ClosedRows) -> None:
        self.time_source, self.closed_rows = time_source, closed_rows
        self.agents, self.rules, self.memories, self.reminders = agents, rules, memories, reminders
        self.outputs = outputs
        self.tasks, self.messages, self.questions = tasks, messages, questions

    def takeover_note(self, event: SessionStarted) -> str:
        return "" if event.source == "compact" else self.other_session_time(event.session)

    def other_session_time(self, session: str) -> str:
        earliest = self.time_source.moment() - TAKEOVER_WINDOW
        rows = self.agents.session_rows(session)
        if rows and rows[0].previous_session_updated_at >= earliest.timestamp():
            return datetime.fromtimestamp(rows[0].previous_session_updated_at).astimezone().strftime("%H:%M")
        peer = self.agents.recent_peer(session, earliest)
        return peer.update_time.astimezone().strftime("%H:%M") if peer else ""

    def rules_numbered(self) -> str:
        return self.numbered(r.text for r in self.rules.all())

    def memories_weighed(self) -> str:
        return "; ".join(self.memory_line(memory) for memory in self.memories.shown())

    def memory_line(self, memory: Memory) -> str:
        closed = self.closed_rows.described(memory.text)
        check = f" [check it still holds: {', '.join(closed)}]" if closed else ""
        return f"{memory.id} (weight {memory.weight}) {memory.text}{check}"

    def reminders_numbered(self) -> str:
        return self.numbered(r.text for r in self.reminders.standing())

    def waiting(self) -> str:
        counts = {"tasks": self.tasks.open_count(), "messages": self.messages.unread_count(), "questions": self.questions.open_count()}
        return ", ".join(f"{n} {name}" for name, n in counts.items() if n)

    def team_history(self, environment: Environment) -> str:
        if not environment.is_session():
            return ""
        return " | ".join(f"{self.writer(m)}: {m.text[:HISTORY_CHARACTERS]}" for m in self.messages.exchanges(HISTORY_MESSAGES))

    @staticmethod
    def writer(message: Message) -> str:
        return message.data.get(Message.TEAMMATE, str(message.author))

    @staticmethod
    def numbered(texts) -> str:
        return "; ".join(f"{n}. {text}" for n, text in enumerate(texts, 1))

    def interrupted_runs(self) -> str:
        cutoff_at = self.time_source.moment() - INTERRUPTION_WINDOW
        return "; ".join(f"output {output.id}, {output.headline()}" for output in self.outputs.recent_interruptions(cutoff_at))
