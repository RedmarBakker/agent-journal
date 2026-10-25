
from journal.db.query import Query
from journal.features.messages.support.hub_mentions import HubMentions
from journal.sync.attachments import Attachments
from journal.http.controllers.controller import Controller
from journal.http.counts import Counts
from journal.http.row_list import RowList
from journal.http.row_list_page import RowListPage
from journal.http.listing import Listing
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.author import Author
from journal.models.message import Message
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.sync.host_desk import HostDesk
from journal.sync.hosts import Hosts
from journal.repositories.messages import Messages
from journal.repositories.reactions import Reactions
from journal.chat.docking import Docking
from journal.models.agent_role import AgentRole
from journal.http.support.comment_target import REPLIED, CommentTarget
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.repositories.links import Links

class MessageController(Controller[Message]):
    """The chat: the user's, the agent's and the journal's messages by id, read a page at a time from the database; the user's are sent from here, as the user, or asked of the environment's host when this journal is not it, and then found by the key the page sent it with once the host has made it."""

    repository: Messages

    def __init__(self, messages: Messages, reactions: Reactions, attachments: Attachments, docking: Docking, agents: Agents, environments: Environments, hosts: Hosts, mentions: HubMentions, links: Links, targets: CommentTarget) -> None:
        self.agents, self.environments, self.hosts, self.mentions, self.links, self.targets = agents, environments, hosts, mentions, links, targets
        self.repository, self.reactions, self.attachments, self.docking = messages, reactions, attachments, docking

    def index(self, request: Request) -> Response:
        if request.query.get("comments"):
            return self.comments_listed(Listing.query_listing(request.query))
        if "on" not in request.query:
            return super().index(request)
        target = self.targets.checked(request.query["on"])
        rows = self.repository.message_replies(target.id) if target.type == REPLIED else self.repository.row_comments(target)
        return Response.json(RowList(rows=self.shown_page(rows), is_last_page=True, counts=Counts(all=len(rows), open=len(rows), unread=0)))

    def comments_listed(self, listing: Listing) -> Response:
        query = self.repository.comments_query()
        page = listing.timeline(self.repository, query, self.closed_rows(query))
        return Response.json(RowList(rows=self.shown_page(page["rows"]), is_last_page=page["is_last_page"], counts=self.counts(query)))

    def listed(self, listing: Listing) -> RowList:
        page = self.chat_page(self.repository.main_chat(), listing)
        unread = self.repository.unviewed()
        counts = Counts(all=self.repository.counted(self.repository.main_chat()), open=len(self.repository.unanswered()) + self.repository.unread_count() + unread, unread=unread)
        return RowList(rows=self.shown_page(page["rows"]), is_last_page=page["is_last_page"], counts=counts)

    def chat_page(self, chat: Query, listing: Listing) -> RowListPage:
        if listing.ids:
            return RowListPage(rows=self.repository.numbered(sorted(listing.ids)), is_last_page=True)
        if listing.cutoff_at:
            return listing.changes(self.repository, chat)
        rows, has_older = self.repository.message_page(chat, listing.limit, listing.upper_id, listing.lower_id)
        return RowListPage(rows=rows, is_last_page=not has_older)

    def agent_chat(self, request: Request) -> Response:
        listing = Listing.query_listing(request.query)
        page = self.chat_page(self.repository.agent_chat(request.params["session"]), listing)
        return Response.json(RowList(rows=self.shown_page(page["rows"]), is_last_page=page["is_last_page"], counts=Counts(all=len(page["rows"]), open=0, unread=0)))

    def shown_page(self, rows: list[Message]) -> list[dict]:
        filed, commented, unanswered = self.repository.linked(Messages.SUBJECT_LINK, [m.row_id for m in rows]), self.repository.linked(Messages.COMMENT_LINK, [m.row_id for m in rows]), {m.id for m in self.repository.unanswered()}
        return [{**ModelFields.build(m), "answered": m.id not in unanswered, "filed": [ref.id for ref in filed.get(m.row_id, [])],
                 "comments_on": [str(ref) for ref in commented.get(m.row_id, [])], "mentions": [str(ref) for ref in self.mentions.found(m.text)]} for m in rows]

    def store(self, request: Request) -> Response:
        if request.body.get("on"):
            return self.comment(self.targets.checked(request.body["on"]), request)
        message = Message(author=Author.USER, text=request.body.get("text", ""), reply_target=request.body.get("reply_target"), idempotency=request.body.get("idempotency", ""))
        environment = self.environments.find(self.repository.scope.id)
        if not self.hosts.is_host(environment):
            self.hosts.ask(environment, HostDesk.MESSAGE, message.host_fields(), request.actor)
            return Response.json({"idempotency": message.idempotency, "notice": self.hosts.waiting_notice(environment)}, 202)
        return Response.json(self.shown(self.repository.posted(message, request.actor)), 201)

    def comment(self, target: Ref, request: Request) -> Response:
        if target.type == REPLIED:
            reply = self.repository.save(Message(author=Author.USER, text=request.body.get("text", ""), reply_target=target.id).arrived(), request.actor)
            return Response.json(self.shown(reply), 201)
        reply_ref = request.body.get("reply_target")
        message = self.repository.save(Message(author=Author.USER, text=request.body.get("text", ""), reply_target=int(reply_ref) if reply_ref else None).arrived(), request.actor)
        self.links.save(Link(source=Ref.build(message), target=target, kind=Messages.COMMENT_LINK), request.actor)
        return Response.json(self.shown(message), 201)

    def sent(self, request: Request) -> Response:
        messages = self.repository.sent_with(request.params["key"])
        return Response.json(self.shown(messages[0])) if messages else Response.absent(f"no message is made with the key {request.params['key']} yet")

    def side_thread(self, request: Request) -> Response:
        return Response.json([self.shown(message) for message in self.repository.side_thread()])

    def side_post(self, request: Request) -> Response:
        message = Message(author=Author.USER, agent_role=AgentRole.PEOPLE, text=request.body.get("text", ""))
        return Response.json(self.shown(self.repository.save(message, request.actor)), 201)

    def read(self, request: Request) -> Response:
        return Response.json(self.shown(self.repository.read(self.repository.find(request.number("id")), request.actor, self._tool_use())))

    def read_all(self, request: Request) -> Response:
        if "ids" not in request.body:
            return Response.json({})
        for id in request.body["ids"]:
            self.repository.read(self.repository.find(int(id)), request.actor, self._tool_use())
        return Response.json({})

    def reply(self, request: Request) -> Response:
        answered = self.repository.find(request.number("id"))
        message = Message(environment_id=answered.environment_id, author=Author.USER, text=request.body.get("text", ""), reply_target=answered.id).arrived()
        return Response.json(self.shown(self.repository.save(message, request.actor)), 201)

    def react(self, request: Request) -> Response:
        produced = self.reactions.toggle(self.repository.find(request.number("id")), request.body.get("emoji", ""), Author.USER, request.actor)
        return Response.json(produced or {})

    def press(self, request: Request) -> Response:
        message = self.repository.find(request.number("id"))
        pressed = [str(label) for label in request.body.get("pressed", [])]
        return Response.json(self.shown(self.repository.save(message.with_merged("data", {"pressed": pressed}), request.actor)))

    def dock(self, request: Request) -> Response:
        return Response.json(self.shown(self.docking.pin_message(self.repository.find(request.number("id")), request.actor)))

    def undock(self, request: Request) -> Response:
        return Response.json(self.shown(self.docking.release(self.repository.find(request.number("id")), request.actor)))

    def attach(self, request: Request) -> Response:
        message = self.repository.find(request.number("id"))
        names = tuple(self.attachments.store(Message.table(), message.row_id, name, data) for name, data in request.files.items())
        saved = self.repository.save(message.with_(files=(*message.files, *names)), request.actor) if names else message
        return Response.json(self.shown(saved))

    def _tool_use(self) -> int:
        agent = self.agents.current()
        return agent.tool_uses if agent else 0
