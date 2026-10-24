from datetime import datetime, timezone

from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.support.actor import Actor
from journal.db.query import Query
from journal.models.agent_role import AgentRole
from journal.models.author import Author
from journal.models.message import Message
from journal.repositories.links import Links
from journal.support.rejection import Rejection
from journal.repositories.agents import Agents
from journal.repositories.reactions import Reactions
from journal.repositories.scope import Scope
from journal.repositories.repository import PAGE_ROWS
from journal.repositories.scoped_repository import ScopedRepository
from journal.repositories.environment_owners import EnvironmentOwners


class Messages(ScopedRepository[Message]):
    ANSWERS = "answers"
    SUBJECT_LINK = "about"
    COMMENT_LINK = "comments_on"

    model = Message

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, reactions: Reactions, links: Links, owners: EnvironmentOwners, agents: Agents) -> None:
        self.owners, self.agents = owners, agents
        super().__init__(connection, bus, scope)
        self.reactions, self.links = reactions, links

    def save(self, row: Message, actor: Actor) -> Message:
        authored = self._placed(row.authored(actor.agent_session()))
        if authored.is_unsaved_user_message() and self.owners.is_colleague(actor, authored.environment_id):
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

    def search(self, terms: list[str]) -> list[Message]:
        return [*self.search_rows(self.main_chat(), terms), *self.search_rows(self.query().filter_unlisted("agent_role", (AgentRole.MAIN,)), terms)]

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

    def unanswered(self) -> list[Message]:
        voiced_at = self.last_message()
        query = self.main_chat().filter(author=Author.USER).filter_present("read_at")
        read = self.selected((query if voiced_at is None else query.filter_greater("read_at", voiced_at)).order("id"))
        return [m for m in read if not m.is_terminal_line and not self.answered(m) and not self.agent_reaction(m)]

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
        prior_items = self.sent_with(message.idempotency) if message.idempotency else []
        return prior_items[0] if prior_items else self.save(message.arrived(), actor)

    def window(self, chat: Query, last: int, previous: int = 0, following: int = 0) -> list[Message]:
        query = chat
        if following:
            query = query.filter_greater("created_at", self.find(following).created_at.isoformat())
        if previous:
            query = query.filter_less("created_at", self.find(previous).created_at.isoformat())
        return list(reversed(self.selected(query.order_descending("created_at").order_descending("id").limit(last))))

    def changes(self, chat: Query, time: datetime, lower_id: int, limit: int) -> list[Message]:
        return list(reversed(self.selected(chat.filter_greater("updated_at", time).filter_greater("id", lower_id).order_descending("id").limit(limit))))

    def unviewed(self) -> int:
        return self.counted(self.main_chat().filter(author=Author.AGENT).filter_null("read_at")) + self.counted(self.main_chat().filter(author=Author.COLLEAGUE).filter_json("data->viewed", 0))

    def visitor_messages(self, share_id: int) -> list[Message]:
        return self.selected(self.query().filter_json("data->share", share_id).order("id"))

    def earliest_commit(self, time: datetime) -> list[Message]:
        return self.selected(self.query().filter_prefix("data->key", "commit:").filter_greater("created_at", time).order("id").limit(1))

    def recent_commits(self, start: datetime, end: datetime, last: int) -> list[Message]:
        return list(reversed(self.selected(self.query().filter_prefix("data->key", "commit:").filter_greater_equal("created_at", start).filter_less("created_at", end).order_descending("id").limit(last))))

    def keyed(self, key: str, actor: Actor) -> list[Message]:
        return self.selected(self.query().filter_json("data->key", key).filter(creator=actor))

    def active_cards(self, ids: list[int]) -> list[Message]:
        return self.selected(self.query().filter_listed("id", ids).filter_json("data->active", True))

    def with_key(self, key: str) -> list[Message]:
        return self.selected(self.query().filter_json("data->key", key))

    def keyed_all(self, key: str, actor: Actor) -> list[Message]:
        return self.selected_globally(self.query().filter_json("data->key", key).filter(creator=actor))

    def replies(self, message: Message) -> list[Message]:
        matched = self.selected(self.main_voice().filter(reply_target=message.id).order("id"))
        linked = [self.find(ref.id) for ref in self.links.sources(message, self.ANSWERS)]
        return sorted([*matched, *linked], key=lambda m: m.row_id)

    def first_reply(self, message: Message) -> Message | None:
        replies = self.replies(message)
        return replies[0] if replies else None

    def recent_replies(self, time: datetime) -> list[Message]:
        return self.selected(self.main_voice().filter_present("reply_target").filter_greater_equal("created_at", time).order("id"))

    def reply_text(self, n: int, text: str) -> list[Message]:
        return self.selected(self.main_voice().filter(reply_target=n, text=text.strip()))

    def recent(self, last: int) -> list[Message]:
        return self.window(self.main_chat(), last)

    def exchanges(self, last: int) -> list[Message]:
        chat = self.main_chat().filter_alternatives(self.query().filter(author=Author.USER), self.query().filter(author=Author.AGENT).filter_present("reply_target"))
        return self.window(chat, last)

    def voice_matches(self, text: str, last: int) -> list[Message]:
        return [message for message in self.recent_voice(last) if message.text == text]

    def comments(self) -> list[Message]:
        commenting = self.link_query.filter(kind=self.COMMENT_LINK).filter_ref("source", self.query())
        written = self.query().filter_alternatives(self.query().filter(author=Author.USER), self.query().filter_present("reply_target"))
        return self.selected(written.filter_existing(commenting).order("id"))

    def recent_voice(self, last: int) -> list[Message]:
        return list(reversed(self.selected(self.main_voice().order_descending("id").limit(last))))

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
