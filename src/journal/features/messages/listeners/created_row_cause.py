from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.messages.support.reply_cause import ReplyCause


class CreatedRowCause(Listener[Created]):
    """A task, plan, document or report the agent creates right after replying to a message of the user's is linked to that message."""

    def __init__(self, cause: ReplyCause) -> None:
        self.cause = cause

    def handle(self, event: Created) -> None:
        self.cause.link(event.model, event.actor)
