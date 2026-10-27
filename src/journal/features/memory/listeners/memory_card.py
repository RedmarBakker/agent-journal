from journal.chat.moment_cards import MomentCards
from journal.models.memory import Memory
from journal.models.model import Model
from journal.models.reminder import Reminder
from journal.models.rule import Rule
from journal.models.support.ref import Ref
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.actor_type import ActorType
from journal.support.card_type import CardType

MEMORY_KINDS = {Memory: ("Memory", CardType.MEMORIES), Rule: ("Rule", CardType.RULES), Reminder: ("Reminder", CardType.REMINDERS)}


class MemoryCard:
    """What a listener of a fact, a rule or a reminder writes in the chat: its noun, number and the verb, and the row it opens; a rule, which is the project's, is shown in the environment of the act."""

    def __init__(self, cards: MomentCards, scope: Scope) -> None:
        self.cards, self.scope = cards, scope

    def show(self, row: Model, actor: Actor, verb: str) -> None:
        if type(row) not in MEMORY_KINDS:
            return
        noun, shows = MEMORY_KINDS[type(row)]
        environment = getattr(row, "environment_id", 0) or self.scope.id
        session = actor.id if actor.kind == ActorType.AGENT else ""
        self.cards.show(environment, session, f"{noun} {row.id} {verb}{self.moment(row)}", "", Ref.build(row), actor=actor, shows=shows)

    @staticmethod
    def moment(row: Model) -> str:
        if isinstance(row, Memory):
            return f", weight {row.weight}"
        return f", due {row.due_at.astimezone().strftime(Reminder.MOMENT)}" if isinstance(row, Reminder) and row.due_at else ""
