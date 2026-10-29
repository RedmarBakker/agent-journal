from dataclasses import asdict

from journal.chat.card_detail import CardDetail
from journal.support.answer_phase import AnswerPhase
from journal.chat.card_category import CardCategory
from journal.models.author import Author
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.support.agent_role import AgentRole
from journal.support.message_thread import MessageThread
from journal.repositories.agents import Agents
from journal.repositories.messages import Messages
from journal.support.actor import Actor
from journal.support.card_type import CardType
from journal.support.card_outcome import CardOutcome
from journal.support.run_place import RunPlace

MOMENT = "moment"


class MomentCards:
    """A card for a moment, in the chat of the agent whose session it names, shown as it was: a task moved, a skill loaded, a check that ran. Each is a new message of the system's. A role card shows in the chat of a session whose agent may not have hooked in yet, such as a reviewer's, and names its role itself."""

    def __init__(self, messages: Messages, agents: Agents, phase: AnswerPhase) -> None:
        self.messages, self.agents, self.phase = messages, agents, phase

    def show(self, environment_id: int, session: str | None, label: str, detail: str = "", row: Ref | None = None, type_name: str = "card", actor: Actor = Actor.system(), key: str = "", command: str = "", *, shows: CardType, outcome: CardOutcome = CardOutcome.NONE, place: RunPlace | None = None) -> Message:
        data = {"kind": type_name, "outcome": str(outcome), "row": str(row) if row else "", "command": command, **(asdict(place) if place else {})}
        return self.show_fields(environment_id, session, label, data, actor, shows, detail, key)

    def show_fields(self, environment_id: int, session: str | None, label: str, data: dict, actor: Actor, shows: CardType, detail: str = "", key: str = "") -> Message:
        roles = self.agents.session_roles(session) if session else []
        return self.show_role_card(roles[0] if roles else AgentRole.MAIN, environment_id, session, label, data, actor, shows, detail, key)

    def show_role_card(self, role: AgentRole, environment_id: int, session: str | None, label: str, data: dict, actor: Actor, shows: CardType, detail: str = "", key: str = "") -> Message:
        data = {"row": "", **data, **CardDetail.parts(detail), **CardCategory.read(label).fields(), "key": key, "shows": str(shows), "card_type": MOMENT}
        card = Message(environment_id=environment_id, author=Author.SYSTEM, session=session or None, thread=MessageThread.agent_thread(role), text=label, data=data)
        self.phase.record_viewer_write(type(self).__name__)
        return self.messages.save(card, actor)

    def is_shown(self, key: str, actor: Actor) -> bool:
        return bool(self.messages.keyed(key, actor))

    def is_key_shown(self, key: str) -> bool:
        return bool(self.messages.with_key(key))
