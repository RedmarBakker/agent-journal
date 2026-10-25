from dataclasses import dataclass
from datetime import datetime

from journal.events.agent.agent_event import AgentEvent
from journal.models.message import Message
from journal.support.voice_key import VoiceKey


@dataclass(frozen=True)
class PeerMessage(AgentEvent):
    """Another session's agent sent the agent a message, read from the agent's transcript: who sent it, by the name it goes by, its words, and the time the transcript names for it, so a transcript read again records it once; it asks for an answer when its last line is a question."""

    sender: str
    text: str
    transcript_time: str = ""

    def message(self, time: datetime) -> Message:
        key = VoiceKey.create("peer", self.session, f"{self.transcript_time}\n{self.sender}\n{self.text}")
        return Message.agent_message(self.sender, self.text, self.session, time, self.is_question()).with_(idempotency=key)

    def is_question(self) -> bool:
        lines = [line for line in self.text.strip().splitlines() if line.strip()]
        return bool(lines) and lines[-1].rstrip().endswith("?")
