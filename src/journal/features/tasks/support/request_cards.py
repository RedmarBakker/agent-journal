from journal.chat.moment_cards import MomentCards
from journal.models.task import Task
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.scope import Scope
from journal.support.card_kind import CardKind
from journal.models.support.ref import Ref


class RequestCards:
    """A mark about a request in the chat of a person's first own environment, shown on their Requests page, and no line to their agent."""

    def __init__(self, cards: MomentCards, owners: EnvironmentOwners, scope: Scope) -> None:
        self.cards, self.owners, self.scope = cards, owners, scope

    def show(self, person: int, task: Task, text: str) -> None:
        homes = [environment for environment in self.owners.owned(person) if environment.is_personal()]
        if not homes:
            return
        with self.scope.environment(homes[0].row_id):
            self.cards.show(homes[0].row_id, None, text, "inbox", row=Ref.build(task), shows=CardKind.REQUESTS)
