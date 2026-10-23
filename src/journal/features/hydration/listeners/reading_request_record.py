from journal.events.agent.session_started import SessionStarted
from journal.events.agent_listener import AgentListener
from journal.repositories.messages import Messages
from journal.support.actor import Actor


class ReadingRequestRecord(AgentListener[SessionStarted]):
    """Once a session has started in an environment whose chat was filled from an earlier conversation, its mark records that the agent was asked to read it, so no later session is asked again."""

    def __init__(self, messages: Messages) -> None:
        self.messages = messages

    def handle(self, event: SessionStarted) -> None:
        for hydration in self.messages.new_hydrations():
            self.messages.save(hydration.with_reading_request(), Actor.system())
