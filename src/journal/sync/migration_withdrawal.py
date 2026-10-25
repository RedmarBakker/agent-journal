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
from journal.sync.environment_withdrawal import EnvironmentWithdrawal

# the shared models that belong to no environment and stay on every journal once the team moves to the hub
KEPT_MODELS = (Rule, Template, Trigger, Check, Sequence)


class MigrationWithdrawal:
    """The withdrawals the move to the hub makes: every environment its owner has not shared taken off the team with everything in it, kept by its owner; then what every journal keeps as its own, its rules, templates, triggers, checks and sequences, those environments' own rows and the links that touch them, kept by all. A row named twice is withdrawn once, as named last."""

    def __init__(self, changes: OutgoingChanges, tables: SharedTables, links: Links, environments: EnvironmentWithdrawal, hooks: ServiceHooks) -> None:
        self.changes, self.tables, self.links, self.environments, self.hooks = changes, tables, links, environments, hooks

    def planned(self, writer: str) -> list[OutgoingChange]:
        private = [environment for environment in self.tables.rows(Environment.table()).rows() if environment.is_private()]
        kept = [*(row for model in KEPT_MODELS for row in self.tables.rows(model.table()).rows()), *private]
        planned = [*(change for environment in private for change in self.environments.changes(environment.row_id, writer)), *(OutgoingChange.withdrawal(row, writer, KEPT_BY_ALL) for row in [*self.links.touching_any(kept), *kept])]
        return list({(change.row_table, change.row): change for change in planned}.values())

    def withdraw(self, actor: Actor) -> None:
        for change in self.planned(actor.stamp):
            self.changes.queued(change, actor)
        self.changes.commit_callback(partial(self.hooks.post, ServiceEvent(CHANGE_QUEUED)))
