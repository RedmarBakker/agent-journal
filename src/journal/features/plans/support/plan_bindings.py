from journal.events.rows.drive_ended import DriveEnded
from journal.models.environment import Environment
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.environments import Environments
from journal.repositories.links import Links
from journal.repositories.scope import BOUND_LINK

ENDED_LINK = "drive_ended"
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.row_labels import RowLabels


class PlanBindings:
    """The hub plans and tasks bound to this machine's environments by a bound_to link, which places in no team and so never leaves the machine: one environment at a time, a second one refused naming who drives it from where. A drive ended, as the row is deleted or closed on another journal or its lease taken over, leaves a drive_ended link in place of its binding, saved with the DriveEnded its environment's agent hears, and that link refuses this machine's writes to the row until it is driven again."""

    def __init__(self, links: Links, environments: Environments, labels: RowLabels) -> None:
        self.links, self.environments, self.labels = links, environments, labels

    def environment_id(self, row: Task | Plan) -> int:
        return next((ref.id for ref in self.links.targets(row, BOUND_LINK)), 0)

    def check(self, row: Task | Plan, environment_id: int) -> None:
        bound = self.environment_id(row)
        if bound and bound != environment_id:
            noun = type(row).__name__.lower()
            raise Rejection(f"{self.labels.name(noun, row)} is driven by {row.driver} from the environment {self.environments.find(bound).name} on this machine: journal {noun} release {row.row_id} there lets it go")

    def bind(self, row: Task | Plan, environment_id: int, actor: Actor) -> None:
        self.check(row, environment_id)
        self.removed(Ref.build(row), ENDED_LINK, actor)
        if not self.environment_id(row):
            self.links.save(Link(source=Ref.build(row), target=Ref(Environment.table(), environment_id), kind=BOUND_LINK), actor)

    def end(self, row: Task | Plan, reason: str, actor: Actor) -> None:
        environment_id = self.environment_id(row)
        noun = type(row).__name__.lower()
        ending = DriveEnded(environment_id=environment_id, row_id=row.row_id, name=self.labels.name(noun, row), noun=noun, reason=reason)
        self.unbind(Ref.build(row), actor)
        self.links.save(Link(source=Ref.build(row), target=Ref(Environment.table(), environment_id), kind=ENDED_LINK).with_event(ending), actor)

    def is_ended(self, row: Task | Plan) -> bool:
        return bool(self.links.targets(row, ENDED_LINK))

    def bound_refs(self) -> list[Ref]:
        return [link.source for link in self.links.unlisted_kind_links(BOUND_LINK)]

    def unbind(self, ref: Ref, actor: Actor) -> None:
        self.removed(ref, BOUND_LINK, actor)

    def removed(self, ref: Ref, kind: str, actor: Actor) -> None:
        for link in self.links.all_matching(source=ref, kind=kind):
            self.links.delete(link, actor)
