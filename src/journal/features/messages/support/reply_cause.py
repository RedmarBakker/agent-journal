
from journal.support.timeout import Timeout
from journal.events.models.updated import Updated
from journal.models.message import Message
from journal.models.model import Model
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.support.actor import Actor
from journal.support.missing_row import MissingRow
from journal.support.time_source import TimeSource

CAUSE_TABLES = ("tasks", "plans", "docs", "reports")
TEXT_FIELDS = ("title", "brief", "body", "abstract")
REPLY_WINDOW_SECONDS = 120


class ReplyCause:
    """Links a task, plan, document or report the agent writes right after replying to one of the user's messages to that message, as `task create --from` and `task edit --from` do: one it creates as created from the message, one it edits as edited from it, so the message's receipt says which."""

    def __init__(self, messages: Messages, links: Links, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.messages, self.links = messages, links

    def created(self, row: Model, actor: Actor) -> None:
        requested_messages = self.requested(row, actor)
        if requested_messages and self.links.sources(row, Messages.SUBJECT_LINK):
            return
        for requested in requested_messages:
            self.links.linked(Ref.build(requested), Ref.build(row), Messages.SUBJECT_LINK, actor)

    def edited(self, event: Updated) -> None:
        if not event.has_changed_fields(TEXT_FIELDS):
            return
        row = event.model
        for requested in self.requested(row, event.actor):
            if Ref.build(row) in self.links.targets(requested, Messages.SUBJECT_LINK):
                continue
            self.links.linked(Ref.build(requested), Ref.build(row), Messages.EDIT_LINK, event.actor)
            self.links.linked(Ref.build(requested), Ref.build(row), Messages.SUBJECT_LINK, event.actor)

    def requested(self, row: Model, actor: Actor) -> list[Message]:
        if not actor.is_agent_actor() or row.table() not in CAUSE_TABLES:
            return []
        reply = self.messages.latest_voice()
        if reply is None or not reply.reply_target or Timeout.seconds(REPLY_WINDOW_SECONDS).started(reply.created_at.timestamp()).is_exceeded(self.time_source.seconds()):
            return []
        try:
            requested = self.messages.find(reply.reply_target)
        except MissingRow:
            return []
        return [requested] if requested.is_user_message() else []
