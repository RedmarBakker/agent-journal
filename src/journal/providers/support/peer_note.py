from dataclasses import dataclass

from journal.events.agent.peer_message import PeerMessage
from journal.models.agent import Agent


@dataclass(frozen=True)
class PeerNote:
    """A message another session's agent sent, as the transcript holds it: who sent it, its words and the time the transcript names for it."""

    sender: str
    text: str
    transcript_time: str = ""

    def event(self, agent: Agent) -> PeerMessage:
        return PeerMessage(sender=self.sender, text=self.text, transcript_time=self.transcript_time, agent=agent)
