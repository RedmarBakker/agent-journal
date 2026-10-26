from journal.events.listener import Listener
from journal.events.models.updated import Updated
from journal.features.messages.support.reply_cause import WRITTEN_FIELDS, ReplyCause


class EditedRowCause(Listener[Updated]):
    """A task, plan, document or report the agent edits right after replying to a message of the user's is linked to that message as edited from it; a change of priority alone is not."""

    def __init__(self, cause: ReplyCause) -> None:
        self.cause = cause

    def handle(self, event: Updated) -> None:
        if any(name in WRITTEN_FIELDS for name in event.changed()):
            self.cause.edited(event.model, event.actor)
