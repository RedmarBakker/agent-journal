from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.support.actor import Actor
from journal.models.author import Author
from journal.models.message import Message
from journal.repositories.messages import Messages
from journal.repositories.secrets import Secrets
from journal.support.time_source import TimeSource
from journal.support.voice_key import VoiceKey


class ExpiryQuestion(AgentListener[Ticked]):
    """A saved browser login that ran out asks the user to log in again, once for each time it runs out."""

    def __init__(self, secrets: Secrets, messages: Messages, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.secrets, self.messages = secrets, messages

    def handle(self, event: Ticked) -> None:
        time = self.time_source.moment()
        for secret in self.secrets.expired_logins(time):
            key = VoiceKey.create("expiry", f"secrets:{secret.id}", str(secret.session_expires))
            self.messages.recorded(Message(author=Author.AGENT, text=f"Your login to {secret.title} has run out: log in again with the Log in button on the Secrets page.\n\nsecret {secret.id}", idempotency=key), Actor.system())
            self.secrets.save(secret.with_(questioned_at=time), Actor.system())
