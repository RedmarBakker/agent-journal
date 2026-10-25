from journal.config import Config
from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent_listener import AgentListener
from journal.support.actor import Actor
from journal.models.author import Author
from journal.models.message import Message
from journal.support.voice_key import VoiceKey
from journal.providers.providers import Providers
from journal.repositories.messages import Messages


class ThoughtRecord(AgentListener[ToolStarting]):
    """Before each tool use, every thought of the agent's turn not yet stored is read from its transcript and stored as a message in the chat, marked as a thought; each carries its idempotency key, so a thought edited since, as amend-links does, is never stored again."""

    def __init__(self, config: Config, providers: Providers, messages: Messages) -> None:
        self.config, self.providers, self.messages = config, providers, messages

    def handle(self, event: ToolStarting) -> None:
        saved = (t.strip() for t in self.providers.lookup(event.provider).turn_thoughts(self.config.root, event.session))
        for thought in dict.fromkeys(t for t in saved if t):
            key = VoiceKey.create("thought", event.session, thought)
            self.messages.recorded(Message(author=Author.AGENT, text=thought, data={"kind": Message.THOUGHT}, idempotency=key), Actor.agent(event.session))
