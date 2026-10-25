from datetime import datetime, timezone

from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.support.actor import Actor
from journal.db.query import Query
from journal.models.agent_role import AgentRole
from journal.models.author import Author
from journal.models.message import TERMINAL_LINE, Message
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.support.rejection import Rejection
from journal.repositories.agents import Agents
from journal.repositories.reactions import Reactions
from journal.repositories.scope import Scope
from journal.repositories.repository import MATCH_ROWS, PAGE_ROWS
from journal.repositories.scoped_repository import ScopedRepository
from journal.repositories.environment_owners import EnvironmentOwners
from journal.support.time_source import TimeSource


# the most rows one page of the chat holds, its written messages and the marks between them together
CHAT_PAGE_ROWS = 400

# the newest cards of one kind looked at by a cleanup at boot
NEWEST_SHOWN = 2000


class Messages(ScopedRepository[Message]):
    ANSWERS = "answers"
    SUBJECT_LINK = "about"
    COMMENT_LINK = "comments_on"

    model = Message

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, reactions: Reactions, links: Links, owners: EnvironmentOwners, agents: Agents, time_source: TimeSource) -> None:
        self.owners, self.agents = owners, agents
        super().__init__(connection, bus, scope, time_source)
        self.reactions, self.links = reactions, links

    def save(self, row: Message, actor: Actor) -> Message:
        authored = self._placed(row.authored(actor.agent_session()))
        if authored.is_unsaved_user_message() and self.owners.is_commenter(actor, authored.environment_id):
            authored = authored.commented(self.owners.person_name(actor.number()), actor.number())
        if authored.is_unsaved_user_message() and self.owners.is_teammate(actor, authored.environment_id):
            authored = authored.with_merged("data", {Message.TEAMMATE: self.owners.person_name(actor.number())})
        if authored.is_new:
            self.check_chat(authored)
        return super().save(authored, actor)

    def check_chat(self, message: Message) -> None:
        if message.author == Author.SYSTEM and not message.data.get("kind"):
            raise Rejection("a system message names its kind, so the chat knows what it shows")
        roles = self.agents.session_roles(message.session) if message.session else []
        if roles and message.agent_role not in roles:
            raise Rejection(f"a message of session {message.session} belongs to its agent's own chat, the {roles[0]} one, not the {message.agent_role} one")

    def unread_comments(self) -> list[Message]:
        return self.selected(self.main_chat().filter(author=Author.COLLEAGUE).filter_null("read_at").order("id"))

    def side_thread(self) -> list[Message]:
        return self.newest(self.query().filter(agent_role=AgentRole.PEOPLE))

    def fold_target(self, card: Message, cutoff_at: datetime) -> list[Message]:
        newest = self.selected_globally(self.main_chat().filter(environment_id=card.environment_id).order_descending("id").limit(1))
        return [message for message in newest if message.takes_fold(card, cutoff_at)]

    def main_chat(self) -> Query:
        return self.query().filter(agent_role=AgentRole.MAIN)

    def agent_chat(self, session: str) -> Query:
        return self.query().filter(session=session).filter_unlisted("agent_role", (AgentRole.MAIN,))

    def main_voice(self) -> Query:
        return self.main_chat().filter(author=Author.AGENT).filter_present("session")

    def search(self, terms: list[str], limit: int = MATCH_ROWS) -> list[Message]:
        chat = self.search_rows(self.main_chat(), terms, limit)
        return [*chat, *self.search_rows(self.query().filter_unlisted("agent_role", (AgentRole.MAIN,)), terms, limit - len(chat))] if len(chat) < limit else chat

    def unread(self) -> list[Message]:
        return self.selected(self.unread_query().order("id").limit(PAGE_ROWS))

    def unread_page_ids(self, count: int) -> list[int]:
        return self.selected_ids(self.unread_query().order("id").limit(count))

    def unread_count(self) -> int:
        return self.counted(self.unread_query())

    def unread_query(self) -> Query:
        return self.main_chat().filter(author=Author.USER).filter_null("read_at")

    def last_user_message(self) -> Message | None:
        return next((m for m in self.selected(self.main_chat().filter(author=Author.USER).order_descending("id").limit(20)) if not m.is_terminal_line), None)

    def unfiled_reads(self, moment: datetime) -> list[Message]:
        read = self.selected(self.main_chat().filter(author=Author.USER).filter_greater("read_at", moment).order("id"))
        return [m for m in read if not m.is_terminal_line and not any(ref.type == "tasks" for ref in self.links.targets(m, self.SUBJECT_LINK))]

    def prompt_repeats(self, text: str) -> list[Message]:
        typed = self.selected(self.main_chat().filter(text=text).filter_json("data->kind", TERMINAL_LINE).order("id"))
        return [*typed, *self.selected(self.main_chat().filter(text=text).filter_json("data->kind", Message.SCHEDULED_PROMPT).order("id"))]

    def unanswered(self) -> list[Message]:
        voiced_at = self.last_message()
        query = self.main_chat().filter(author=Author.USER).filter_present("read_at")
        read = self.selected((query if voiced_at is None else query.filter_greater("read_at", voiced_at)).without("text").order("id"))
        return [m for m in read if not m.is_terminal_line and not self.answered(m) and not self.agent_reaction(m)]

    def latest_voice(self) -> Message | None:
        return next(iter(self.selected(self.main_voice().order_descending("id").limit(1))), None)

    def last_message(self) -> str | None:
        return self.maximum(self.main_voice().filter(acknowledgement=False).filter_unequal("data->kind", Message.THOUGHT), "created_at", None)

    def answered(self, message: Message) -> bool:
        return bool(self.selected_globally(self.main_voice().filter(reply_target=message.id).limit(1))) or bool(self.links.sources(message, self.ANSWERS))

    def agent_reaction(self, message: Message) -> bool:
        return any(r.author == Author.AGENT for r in self.reactions.reactions(message))

    def peer_questions(self) -> list[Message]:
        questions = self.selected(self.query().filter_json("data->kind", Message.PEER).filter_json("data->asks", 1).order("id"))
        return [question for question in questions if not self.selected(self.query().filter_json("data->sent_to", question.data[Message.PEER]).filter_greater("id", question.id).limit(1))]

    def sent_with(self, key: str) -> list[Message]:
        return self.selected(self.query().filter(idempotency=key).order("id").limit(1))

    def posted(self, message: Message, actor: Actor) -> Message:
        return self.recorded(message.arrived(), actor) if message.idempotency else self.save(message.arrived(), actor)

    def recorded(self, message: Message, actor: Actor) -> Message:
        with self.writing():
            prior = self.sent_with(message.idempotency)
            return prior[0] if prior else self.save(message, actor)

    def window(self, chat: Query, last: int, previous: int = 0, following: int = 0) -> list[Message]:
        return self.latest_rows(self.bounded(chat, previous, following), last)

    # a page of the chat: its newest messages down to the count-th a person or an agent wrote, every mark between them with them, and
    # whether a written message older than those is left
    def message_page(self, chat: Query, count: int, previous: int = 0, following: int = 0) -> tuple[list[Message], bool]:
        query = self.bounded(chat, previous, following)
        person_messages = self.latest_rows(query.filter_unequal("author", Author.SYSTEM.value), count + 1)
        if len(person_messages) <= count:
            return self.latest_rows(query, CHAT_PAGE_ROWS), False
        oldest = person_messages[1]
        return self.latest_rows(query.filter_greater_equal("created_at", oldest.created_at.isoformat()), CHAT_PAGE_ROWS), True

    def bounded(self, chat: Query, previous: int, following: int) -> Query:
        query = chat
        if following:
            query = query.filter_greater("created_at", self.find(following).created_at.isoformat())
        if previous:
            query = query.filter_less("created_at", self.find(previous).created_at.isoformat())
        return query

    def latest_rows(self, query: Query, last: int) -> list[Message]:
        return list(reversed(self.selected(query.order_descending("created_at").order_descending("id").limit(last))))

    def unviewed(self) -> int:
        return self.counted(self.main_chat().filter(author=Author.AGENT).filter_null("read_at")) + self.counted(self.main_chat().filter(author=Author.COLLEAGUE).filter_json("data->viewed", 0))

    def visitor_messages(self, share_id: int) -> list[Message]:
        return self.selected(self.query().filter_json("data->share", share_id).order("id"))

    def earliest_commit(self, time: datetime) -> list[Message]:
        return self.selected(self.query().filter_prefix("data->key", "commit:").filter_greater("created_at", time).order("id").limit(1))

    def recent_commits(self, start: datetime, end: datetime, last: int) -> list[Message]:
        return list(reversed(self.selected(self.query().filter_prefix("data->key", "commit:").filter_greater_equal("created_at", start).filter_less("created_at", end).order_descending("id").limit(last))))

    # the messages a person or an agent wrote, in every environment, leaving out the journal's own marks and cards
    def message_count(self) -> int:
        return self.stored_matching_count(self.query().filter_listed("author", [Author.USER.value, Author.AGENT.value, Author.COLLEAGUE.value]))

    def keyed(self, key: str, actor: Actor) -> list[Message]:
        return self.selected(self.query().filter_json("data->key", key).filter(creator=actor))

    def active_cards(self, ids: list[int]) -> list[Message]:
        return self.selected(self.query().filter_listed("id", ids).filter_json("data->active", True))

    def with_key(self, key: str) -> list[Message]:
        return self.selected(self.query().filter_json("data->key", key))

    def keyed_all(self, key: str, actor: Actor) -> list[Message]:
        return self.selected_globally(self.query().filter_json("data->key", key).filter(creator=actor))

    def message_replies(self, message_id: int) -> list[Message]:
        return self.selected(self.main_chat().filter(reply_target=message_id).order("id"))

    def replies(self, message: Message) -> list[Message]:
        matched = self.selected(self.main_voice().filter(reply_target=message.id).order("id"))
        linked = [self.find(ref.id) for ref in self.links.sources(message, self.ANSWERS)]
        return sorted([*matched, *linked], key=lambda m: m.row_id)

    def first_reply(self, message: Message) -> Message | None:
        replies = self.replies(message)
        return replies[0] if replies else None

    def recent_replies(self, time: datetime) -> list[Message]:
        return self.selected(self.main_voice().filter_present("reply_target").filter_greater_equal("created_at", time).order("created_at").order("id"))

    def recent(self, last: int) -> list[Message]:
        return self.window(self.main_chat(), last)

    def exchanges(self, last: int) -> list[Message]:
        chat = self.main_chat().filter_alternatives(self.query().filter(author=Author.USER), self.query().filter(author=Author.AGENT).filter_present("reply_target"))
        return self.window(chat, last)

    def comments_query(self) -> Query:
        return self.comment_query(self.link_query.filter(kind=self.COMMENT_LINK))

    def row_comments(self, ref: Ref) -> list[Message]:
        return self.selected(self.comment_query(self.link_query.filter(kind=self.COMMENT_LINK, target=str(ref))).order("id"))

    def comment_query(self, links: Query) -> Query:
        candidates = self.query().filter_alternatives(self.query().filter(author=Author.USER), self.query().filter_present("reply_target"))
        return candidates.filter_existing(links.filter_ref("source", self.query()))

    def new_hydrations(self) -> list[Message]:
        return self.selected(self.query().filter_json("data->kind", Message.HYDRATION).filter_json("data->reading_request", False).order("id"))

    def thoughts(self, session: str, last: int = 60) -> list[Message]:
        rows = self.selected(self.query().filter(creator=Actor.agent(session)).filter_json("data->kind", Message.THOUGHT).order_descending("id").limit(last))
        return list(reversed(rows))

    def read(self, message: Message, actor: Actor, tool_use: int) -> Message:
        if self.owners.is_colleague(actor, message.environment_id):
            return message
        if message.is_comment() and actor.is_user():
            return self.save(message.viewed(), actor) if not message.data.get(Message.VIEWED) else message
        return message if message.read_at else self.save(message.with_(read_at=datetime.now(timezone.utc), read_position=tool_use), actor)

    def newest_shown(self, kind: str) -> list[Message]:
        return self.selected(self.query().filter_json("data->shows", kind).order_descending("id").limit(NEWEST_SHOWN))

