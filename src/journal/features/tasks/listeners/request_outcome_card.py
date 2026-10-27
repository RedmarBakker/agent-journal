from journal.events.listener import Listener
from journal.events.models.synced_update import SyncedUpdate
from journal.features.tasks.support.request_cards import RequestCards
from journal.models.task import Task
from journal.support.actor import Actor
from journal.support.row_labels import RowLabels
from journal.sync.team_account import TeamAccount


class RequestOutcomeCard(Listener[SyncedUpdate]):
    """A request this journal's person filed that its recipient finished or turned down is a mark in the chat of their first own environment, with the reason when it was declined."""

    def __init__(self, cards: RequestCards, labels: RowLabels, account: TeamAccount) -> None:
        self.cards, self.labels, self.account = cards, labels, account

    def handle(self, event: SyncedUpdate) -> None:
        task, before = event.model, event.previous
        person = self.account.user_number()
        if not (isinstance(task, Task) and isinstance(before, Task) and task.creator == Actor.user(person) and task.state != before.state):
            return
        name = self.labels.name("task", task)
        if task.is_declined():
            self.cards.show(person, task, f"{name} was declined: {task.outcome.removeprefix('declined: ')}")
        elif task.is_completed():
            self.cards.show(person, task, f"{name} is completed: {task.title}")
