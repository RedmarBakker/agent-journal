from functools import partial

from journal.models.check import Check
from journal.models.environment import Environment
from journal.models.outgoing_change import KEPT_BY_ALL, OutgoingChange
from journal.models.rule import Rule
from journal.models.sequence import Sequence
from journal.models.template import Template
from journal.models.trigger import Trigger
from journal.repositories.links import Links
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.repositories.shared_tables import SharedTables
from journal.services.service_event import CHANGE_QUEUED, ServiceEvent
from journal.services.service_hooks import ServiceHooks
from journal.support.actor import Actor

# the shared models that belong to no environment and stay on every journal once the team moves to the hub
KEPT_MODELS = (Rule, Template, Trigger, Check, Sequence)


class MigrationWithdrawal:
    """The withdrawal the move to the hub makes of what every journal keeps as its own: its rules, templates, triggers, checks and sequences, the row of every environment its owner has not shared, and the links that touch them, each queued for the team server as withdrawn and kept by all, so the server forgets them and every journal keeps its copy."""

    def __init__(self, changes: OutgoingChanges, tables: SharedTables, links: Links, hooks: ServiceHooks) -> None:
        self.changes, self.tables, self.links, self.hooks = changes, tables, links, hooks

    def withdraw(self, actor: Actor) -> None:
        rows = [*(row for model in KEPT_MODELS for row in self.tables.rows(model.table()).rows()), *(environment for environment in self.tables.rows(Environment.table()).rows() if environment.is_private())]
        for row in [*self.links.touching_any(rows), *rows]:
            self.changes.queued(OutgoingChange.withdrawal(row, actor.stamp, KEPT_BY_ALL), actor)
        self.changes.commit_callback(partial(self.hooks.post, ServiceEvent(CHANGE_QUEUED)))
