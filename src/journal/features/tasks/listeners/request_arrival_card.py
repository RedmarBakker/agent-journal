from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.tasks.support.hub_filer import REQUESTER_LINK
from journal.features.tasks.support.request_cards import RequestCards
from journal.models.link import Link
from journal.repositories.tasks import Tasks
from journal.support.row_labels import RowLabels
from journal.sync.team_account import TeamAccount


class RequestArrivalCard(Listener[Created]):
    """A request filed for this journal's person is a mark in the chat of their first own environment, and no line to their agent."""

    def __init__(self, cards: RequestCards, tasks: Tasks, labels: RowLabels, account: TeamAccount) -> None:
        self.cards, self.tasks, self.labels, self.account = cards, tasks, labels, account

    def handle(self, event: Created) -> None:
        link = event.model
        person = self.account.user_number()
        if not (isinstance(link, Link) and link.kind == REQUESTER_LINK and link.target.id == person):
            return
        for task in self.tasks.tasks_numbered([link.source.id]):
            self.cards.show(person, task, f"{self.labels.name('task', task)} is a request for you: {task.title}")
