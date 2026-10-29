from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.sequences.support.phrase_starts import PhraseStarts
from journal.models.message import Message
from journal.repositories.agents import Agents


class MessagePhraseStart(Listener[Created]):
    """A message of the user's in the chat that is a sequence's phrase starts that sequence for the agent here."""

    def __init__(self, starts: PhraseStarts, agents: Agents) -> None:
        self.starts, self.agents = starts, agents

    def handle(self, event: Created) -> None:
        message = event.model
        if not isinstance(message, Message) or not message.is_user_message() or message.is_terminal_line:
            return
        agent = self.agents.current()
        if agent is not None:
            self.starts.start(message.text, agent.session, message.environment_id)
