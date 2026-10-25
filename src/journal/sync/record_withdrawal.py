from functools import partial

from journal.events.listener import Listener
from journal.events.rows.environment_unshared import EnvironmentUnshared
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.services.service_event import CHANGE_QUEUED, ServiceEvent
from journal.services.service_hooks import ServiceHooks
from journal.support.actor import Actor
from journal.sync.environment_withdrawal import EnvironmentWithdrawal
from journal.sync.team_account import TeamAccount


class RecordWithdrawal(Listener[EnvironmentUnshared]):
    """An environment taken back from the team is queued for the team server as withdrawn, kept by its owner, so the server and every colleague's journal let go of its rows and the owner's journals keep theirs."""

    def __init__(self, changes: OutgoingChanges, account: TeamAccount, withdrawal: EnvironmentWithdrawal, hooks: ServiceHooks) -> None:
        self.changes, self.account, self.withdrawal, self.hooks = changes, account, withdrawal, hooks

    def handle(self, event: EnvironmentUnshared) -> None:
        if not self.account.is_joined():
            return
        actor = Actor.parse(event.actor)
        for change in self.withdrawal.changes(event.environment_id, actor.stamp):
            self.changes.queued(change, actor)
        self.changes.commit_callback(partial(self.hooks.post, ServiceEvent(CHANGE_QUEUED)))
