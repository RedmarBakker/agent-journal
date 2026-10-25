from datetime import datetime, timedelta, timezone

from journal.models.author import Author
from journal.models.link import Link
from journal.models.model import Model
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.support.actor import Actor
from journal.support.actor_kind import ActorKind
from journal.support.missing_row import MissingRow

CAUSED_TABLES = ("tasks", "plans", "docs", "reports")
WRITTEN_FIELDS = ("title", "brief", "priority", "body", "abstract")
RIGHT_AFTER_SECONDS = 120


class ReplyCause:
    """Links a task, plan, document or report the agent writes right after replying to one of the user's messages to that message, as `task create --from` does, so the message shows it."""

    def __init__(self, messages: Messages, links: Links) -> None:
        self.messages, self.links = messages, links

    def link(self, row: Model, actor: Actor) -> None:
        if actor.kind != ActorKind.AGENT or row.table() not in CAUSED_TABLES:
            return
        reply = self.messages.latest_voice()
        if reply is None or not reply.reply_target or datetime.now(timezone.utc) - reply.created_at > timedelta(seconds=RIGHT_AFTER_SECONDS):
            return
        try:
            requested = self.messages.find(reply.reply_target)
        except MissingRow:
            return
        if requested.author == Author.USER and Ref.build(row) not in self.links.targets(requested, Messages.SUBJECT_LINK):
            self.links.save(Link(source=Ref.build(requested), target=Ref.build(row), kind=Messages.SUBJECT_LINK), actor)
