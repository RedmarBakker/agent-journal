from journal.config import Config
from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent_listener import AgentListener
from journal.support.actor import Actor
from journal.models.author import Author
from journal.models.message import RECORDED_TEXT, Message
from journal.providers.providers import Providers
from journal.repositories.messages import Messages


class ThoughtRecord(AgentListener[ToolStarting]):
    """Before each tool use, every thought of the agent's turn not yet stored is read from its transcript and stored as a message in the chat, marked as a thought; a thought edited since, as amend-links does, is known by the text it was stored with."""

    def __init__(self, config: Config, providers: Providers, messages: Messages) -> None:
        self.config, self.providers, self.messages = config, providers, messages

    def handle(self, event: ToolStarting) -> None:
        stored = {text for m in self.messages.thoughts(event.session) for text in (m.text, m.data.get(RECORDED_TEXT)) if text}
        saved = (t.strip() for t in self.providers.lookup(event.provider).turn_thoughts(self.config.root, event.session))
        for thought in dict.fromkeys(t for t in saved if t and t not in stored):
            self.messages.save(Message(author=Author.AGENT, text=thought, data={"kind": Message.THOUGHT}), Actor.agent(event.session))
