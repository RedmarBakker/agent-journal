from datetime import datetime, timedelta, timezone

from journal.models.author import Author
from journal.models.model import Model
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.support.actor import Actor
from journal.support.actor_kind import ActorKind
from journal.support.missing_row import MissingRow
from journal.support.time_source import TimeSource

CAUSED_TABLES = ("tasks", "plans", "docs", "reports")
WRITTEN_FIELDS = ("title", "brief", "priority", "body", "abstract")
RIGHT_AFTER_SECONDS = 120


class ReplyCause:
    """Links a task, plan, document or report the agent writes right after replying to one of the user's messages to that message, as `task create --from` does, so the message shows it."""

    def __init__(self, messages: Messages, links: Links, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.messages, self.links = messages, links

    def link(self, row: Model, actor: Actor) -> None:
        if actor.kind != ActorKind.AGENT or row.table() not in CAUSED_TABLES:
            return
        reply = self.messages.latest_voice()
        if reply is None or not reply.reply_target or self.time_source.moment() - reply.created_at > timedelta(seconds=RIGHT_AFTER_SECONDS):
            return
        try:
            requested = self.messages.find(reply.reply_target)
        except MissingRow:
            return
        if requested.author == Author.USER:
            self.links.linked(Ref.build(requested), Ref.build(row), Messages.SUBJECT_LINK, actor)
