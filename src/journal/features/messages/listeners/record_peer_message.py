from datetime import datetime, timezone

from journal.events.agent.peer_message import PeerMessage
from journal.events.agent_listener import AgentListener
from journal.support.actor import Actor
from journal.repositories.messages import Messages
from journal.support.time_source import TimeSource


class RecordPeerMessage(AgentListener[PeerMessage]):
    """A message another session's agent sent to this one reaches the chat as that agent's, written by it as an external agent, never as the user's words; whether it arrived as a prompt or mid-turn."""

    def __init__(self, messages: Messages, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.messages = messages

    def handle(self, event: PeerMessage) -> None:
        self.messages.save(event.message(self.time_source.moment()), Actor.external(event.sender))
