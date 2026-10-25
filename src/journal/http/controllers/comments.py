from journal.http.row_list_page import RowListPage
from journal.http.listing import Listing
from journal.http.counts import Counts
from journal.db.query import Query
from journal.http.controllers.controller import Controller
from journal.http.row_list import RowList
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.author import Author
from journal.models.link import Link
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.support.rejection import Rejection
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.repositories.rows import Rows

COMMENTED = ("tasks", "plans", "docs", "reports", "facts", "rules", "reminders", "questions", "messages")
# a comment under a chat message is a reply to it, never a link
REPLIED = "messages"


class CommentController(Controller[Message]):
    """A comment written under a row in the viewer is a message from the user linked to the row as comments_on, shown under it; it reaches the agent as any message does; one under a chat message is a reply to that message. Their list is the messages alone, or with on=tasks:12 every comment under that row; one read by id names the row it is under."""

    def __init__(self, messages: Messages, links: Links, rows: Rows) -> None:
        self.repository, self.links, self.references = messages, links, rows

    def index(self, request: Request) -> Response:
        if "on" not in request.query:
            return super().index(request)
        target = self.row(request.query["on"])
        rows = self.repository.message_replies(target.id) if target.type == REPLIED else self.repository.row_comments(target)
        return Response.json(RowList(rows=self.shown_page(rows), is_last_page=True, counts=Counts(all=len(rows), open=len(rows), unread=0)))

    def list_query(self) -> Query:
        return self.repository.comments_query()

    def list_page(self, listing: Listing, query: Query) -> RowListPage:
        return listing.timeline(self.repository, query, self.closed_rows(query))

    def shown_page(self, rows: list[Message]) -> list[dict]:
        enabled = self.repository.linked(Messages.COMMENT_LINK, [m.row_id for m in rows])
        return [{**ModelFields.build(m), "on": [str(ref) for ref in enabled.get(m.row_id, [])]} for m in rows]

    def store(self, request: Request) -> Response:
        target = self.row(request.body.get("on", ""))
        if target.type == REPLIED:
            return self.reply(target, request)
        reply_ref = request.body.get("reply_target")
        message = self.repository.save(Message(author=Author.USER, text=request.body.get("text", ""), reply_target=int(reply_ref) if reply_ref else None).arrived(), request.actor)
        self.links.save(Link(source=Ref.build(message), target=target, kind=Messages.COMMENT_LINK), request.actor)
        return Response.json(self.shown(message), 201)

    def reply(self, target: Ref, request: Request) -> Response:
        message = self.repository.save(Message(author=Author.USER, text=request.body.get("text", ""), reply_target=target.id).arrived(), request.actor)
        return Response.json(self.shown(message), 201)

    def row(self, reference: object) -> Ref:
        matched = str(reference)
        kind, _, id = matched.partition(":")
        if kind not in COMMENTED or not id.isdigit() or not self.references.is_row(Ref(kind, int(id))):
            raise Rejection(f"a comment is written under a task, a plan, a document, a report, a fact, a rule, a reminder, a question or a chat message that is there, named as tasks:12, not {matched!r}")
        return Ref(kind, int(id))
