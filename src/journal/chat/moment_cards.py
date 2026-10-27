from dataclasses import asdict
from datetime import datetime, timedelta, timezone

from journal.chat.card_detail import CardDetail
from journal.chat.card_category import CardCategory
from journal.repositories.setting_rows import SettingRows
from journal.support.option import Option
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
from journal.support.time_source import TimeSource

MOMENT = "moment"
FOLD_SECONDS = Option("messages.fold_marks_seconds", "Fold marks of one kind within", "Seconds within which a chat mark of the same kind as the chat's newest message, a mark too, is counted in it instead of posted", 10, unit="seconds")


class MomentCards:
    """A card for a moment, in the chat of the agent whose session it names, shown as it was: a task moved, a skill loaded, a check that ran. Each is a new message of the system's, save one of a kind that folds, posted within the fold window after a mark of its kind that is the chat's newest message, which is counted in that mark with its detail. A role card shows in the chat of a session whose agent may not have hooked in yet, such as a reviewer's, and names its role itself."""

    def __init__(self, messages: Messages, settings: SettingRows, agents: Agents, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.messages, self.settings, self.agents = messages, settings, agents

    def show(self, environment_id: int, session: str | None, label: str, detail: str = "", row: Ref | None = None, kind: str = "card", actor: Actor = Actor.system(), key: str = "", command: str = "", *, shows: CardType, outcome: CardOutcome = CardOutcome.NONE, place: RunPlace | None = None) -> Message:
        data = {"kind": kind, "outcome": str(outcome), "row": str(row) if row else "", "command": command, **(asdict(place) if place else {})}
        return self.show_fields(environment_id, session, label, data, actor, shows, detail, key)

    def show_fields(self, environment_id: int, session: str | None, label: str, data: dict, actor: Actor, shows: CardType, detail: str = "", key: str = "") -> Message:
        roles = self.agents.session_roles(session) if session else []
        return self.show_role_card(roles[0] if roles else AgentRole.MAIN, environment_id, session, label, data, actor, shows, detail, key)

    def show_role_card(self, role: AgentRole, environment_id: int, session: str | None, label: str, data: dict, actor: Actor, shows: CardType, detail: str = "", key: str = "") -> Message:
        data = {"row": "", **data, **CardDetail.parts(detail), **CardCategory.read(label).fields(), "key": key, "shows": str(shows), "card_type": MOMENT}
        card = Message(environment_id=environment_id, author=Author.SYSTEM, session=session or None, thread=MessageThread.agent_thread(role), text=label, data=data)
        cutoff_at = self.time_source.moment() - timedelta(seconds=self.settings.decimal(FOLD_SECONDS))
        foldable = self.messages.fold_target(card, cutoff_at) if shows.folds() else []
        return self.messages.save(foldable[0].folded(label, detail) if foldable else card, actor)

    def is_shown(self, key: str, actor: Actor) -> bool:
        return bool(self.messages.keyed(key, actor))

    def is_key_shown(self, key: str) -> bool:
        return bool(self.messages.with_key(key))
