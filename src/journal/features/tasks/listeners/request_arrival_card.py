from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.tasks.support.hub_filing import REQUESTED_OF
from journal.models.link import Link
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.tasks import Tasks
from journal.support.card_kind import CardKind
from journal.support.row_labels import RowLabels
from journal.sync.team_account import TeamAccount


class RequestArrivalCard(Listener[Created]):
    """A request filed for this journal's person is a mark in the chat of their first own environment, and no line to their agent."""

    def __init__(self, cards: MomentCards, owners: EnvironmentOwners, tasks: Tasks, labels: RowLabels, account: TeamAccount) -> None:
        self.cards, self.owners, self.tasks, self.labels, self.account = cards, owners, tasks, labels, account

    def handle(self, event: Created) -> None:
        link = event.model
        person = self.account.user_number()
        if not (isinstance(link, Link) and link.kind == REQUESTED_OF and link.target.id == person):
            return
        homes = [environment for environment in self.owners.owned(person) if environment.is_personal()]
        for task in self.tasks.numbered_anywhere([link.source.id]) if homes else []:
            self.cards.show(homes[0].row_id, None, f"{self.labels.name('task', task)} is a request for you: {task.title}", "inbox", row=link.source, shows=CardKind.REQUESTS)
