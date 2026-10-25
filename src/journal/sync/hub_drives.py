import time
from typing import Callable

from journal.features.plans.support.plan_bindings import PlanBindings
from journal.models.environment import Environment
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.actor_kind import ActorKind
from journal.support.rejection import Rejection
from journal.support.row_labels import RowLabels
from journal.sync.hosting import Hosting
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_requests import TeamRequests
from journal.sync.team_server_link import TeamServerLink
from sync_server.lease import Lease

DRIVE_LAPSE_SECONDS = 15 * 60
RENEW_SECONDS = 60


class HubDrives:
    """The hub plans and tasks this machine drives, each from one of its environments: a drive takes the team server's lease of the row, refused while another device holds it, lapsed or not, renewed here every minute and lapsing 15 minutes after its last renewal, when a takeover alone has it; it binds the row to the environment in scope and writes on the hub row the person and the agent driving it, and a release undoes all three. A drive ends here when its lease is found taken over at a renewal, or its row is deleted or closed on another journal: the binding is lost, the environment's agent told why, naming who, and this machine's writes to the row refused until it is driven again. The hosted journal drives nothing."""

    def __init__(self, link: TeamServerLink, bindings: PlanBindings, tasks: Tasks, plans: Plans, environments: Environments, scope: Scope, hosting: Hosting, labels: RowLabels, owners: EnvironmentOwners) -> None:
        self.link, self.bindings, self.environments, self.scope, self.hosting, self.labels = link, bindings, environments, scope, hosting, labels
        self.owners = owners
        self.repositories = {Task: tasks, Plan: plans}
        self.tables = {Task.table(): tasks, Plan.table(): plans}
        self.renewed_at = 0.0

    def drive(self, row: Task | Plan, actor: Actor) -> Task | Plan:
        return self.driven(row, lambda name: self.link.acquire_free_lease(name, DRIVE_LAPSE_SECONDS), actor)

    def takeover(self, row: Task | Plan, actor: Actor) -> Task | Plan:
        return self.driven(row, lambda name: self.link.takeover_lease(name, DRIVE_LAPSE_SECONDS), actor)

    def release(self, row: Task | Plan, actor: Actor) -> Task | Plan:
        if not self.bindings.environment_id(row):
            raise Rejection(f"{self.label(row)} is not driven from this machine")
        ref = Ref.build(row)
        lease = TeamRequests.reached(lambda: self.link.release_lease(self.lease_name(ref)))
        self.bindings.unbind(ref, actor)
        return row if lease.holder else self.repositories[type(row)].save(row.with_(driver="", driver_agent=""), actor)

    def renew(self) -> None:
        if time.monotonic() - self.renewed_at < RENEW_SECONDS:
            return
        self.renewed_at = time.monotonic()
        for ref in self.bindings.bound_refs():
            self.renewed(ref)

    def renewed(self, ref: Ref) -> None:
        try:
            self.link.acquire_free_lease(self.lease_name(ref), DRIVE_LAPSE_SECONDS)
        except TeamRefusal:
            holder = self.link.lease_state(self.lease_name(ref))
            self.bindings.end(self.tables[ref.type].find(ref.id), f"{holder.holder} took it over on {holder.device_name}", Actor.system())


    def doer(self, actor: Actor) -> str:
        return self.owners.person_name(int(actor.id)) if actor.kind == ActorKind.USER else "someone"

    def driven(self, row: Task | Plan, lease_request: Callable[[str], Lease], actor: Actor) -> Task | Plan:
        environment = self.drivable(row)
        lease = TeamRequests.reached(lambda: self.leased(row, lease_request))
        self.bindings.bind(row, environment.row_id, actor)
        return self.repositories[type(row)].save(row.with_(driver=lease.holder, driver_agent=f"the agent of {environment.name} on {lease.device_name}"), actor)

    def drivable(self, row: Task | Plan) -> Environment:
        if self.hosting.is_hosted():
            raise Rejection("the hosted journal runs no agent, so it drives nothing: drive from a journal of your own")
        if row.environment_id not in self.environments.hub_ids():
            raise Rejection(f"{self.label(row)} is not the hub's: only a hub plan or task is driven")
        environment = self.environments.find(self.scope.id)
        if not environment.is_personal():
            raise Rejection(f"{self.label(row)} is driven from an environment of your own, never the hub or the Team chat")
        self.bindings.check(row, environment.row_id)
        return environment

    def leased(self, row: Task | Plan, lease_request: Callable[[str], Lease]) -> Lease:
        try:
            return lease_request(self.lease_name(Ref.build(row)))
        except TeamRefusal as refused:
            noun = type(row).__name__.lower()
            raise Rejection(f"{self.label(row)} is driven from another machine: {refused}; journal {noun} drive {row.row_id} --take-over has it once its lease lapses, {DRIVE_LAPSE_SECONDS // 60} minutes after its last renewal") from refused

    def drive_line(self, row: Task | Plan) -> str:
        return f"{self.label(row)} is driven from here by {row.driver}, {row.driver_agent}; its lease is renewed every minute while this journal runs and lapses {DRIVE_LAPSE_SECONDS // 60} minutes after its last renewal"

    def release_line(self, row: Task | Plan) -> str:
        return f"{self.label(row)} is released: anyone may drive it"

    def label(self, row: Task | Plan) -> str:
        return self.labels.name(type(row).__name__.lower(), row)

    @staticmethod
    def lease_name(ref: Ref) -> str:
        return f"drive:{ref}"
