from datetime import datetime, timedelta, timezone

from journal.models.author import Author
from journal.models.message import Message
from journal.models.model import Model
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.support.actor import Actor
from journal.support.actor_type import ActorType
from journal.support.missing_row import MissingRow
from journal.support.time_source import TimeSource

CAUSED_TABLES = ("tasks", "plans", "docs", "reports")
WRITTEN_FIELDS = ("title", "brief", "body", "abstract")
REPLY_WINDOW_SECONDS = 120


class ReplyCause:
    """Links a task, plan, document or report the agent writes right after replying to one of the user's messages to that message, as `task create --from` and `task edit --from` do: one it creates as created from the message, one it edits as edited from it, so the message's receipt says which."""

    def __init__(self, messages: Messages, links: Links, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.messages, self.links = messages, links

    def created(self, row: Model, actor: Actor) -> None:
        for requested in self.requested(row, actor):
            self.links.linked(Ref.build(requested), Ref.build(row), Messages.SUBJECT_LINK, actor)

    def edited(self, row: Model, actor: Actor) -> None:
        for requested in self.requested(row, actor):
            if Ref.build(row) in self.links.targets(requested, Messages.SUBJECT_LINK):
                continue
            self.links.linked(Ref.build(requested), Ref.build(row), Messages.EDIT_LINK, actor)
            self.links.linked(Ref.build(requested), Ref.build(row), Messages.SUBJECT_LINK, actor)

    def requested(self, row: Model, actor: Actor) -> list[Message]:
        if actor.actor_type != ActorType.AGENT or row.table() not in CAUSED_TABLES:
            return []
        reply = self.messages.latest_voice()
        if reply is None or not reply.reply_target or self.time_source.moment() - reply.created_at > timedelta(seconds=REPLY_WINDOW_SECONDS):
            return []
        try:
            requested = self.messages.find(reply.reply_target)
        except MissingRow:
            return []
        return [requested] if requested.author == Author.USER else []
