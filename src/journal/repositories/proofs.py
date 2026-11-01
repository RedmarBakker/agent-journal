from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.models.proof import Proof
from journal.models.proof_state import ProofState
from journal.models.task import Task
from journal.repositories.linked_rows import LinkedRows
from journal.repositories.links import Links
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.time_source import TimeSource

PROOF_LINK = "proves"
PROVED_STATES = (ProofState.SHOWN, ProofState.CHECKED)
CHECKED_STATES = (ProofState.CHECKED, ProofState.CHECKED_UNFINISHED)


class Proofs(ScopedRepository[Proof], LinkedRows):
    link_kind = PROOF_LINK
    model = Proof

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, links: Links, time_source: TimeSource) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.links = links

    def task_proofs(self, task: Task) -> list[Proof]:
        return sorted(self.children(task), key=lambda proof: proof.point)

    def is_proved(self, task: Task) -> bool:
        latest = {proof.point: proof for proof in sorted(self.children(task), key=lambda proof: proof.row_id)}
        return all(point in latest and latest[point].state in PROVED_STATES for point in range(1, len(task.points()) + 1))

    def is_checked(self, task: Task) -> bool:
        latest = {proof.point: proof for proof in sorted(self.children(task), key=lambda proof: proof.row_id)}
        return all(point in latest and latest[point].state in CHECKED_STATES for point in range(1, len(task.points()) + 1))

    def is_checkable(self, task: Task) -> bool:
        return task.delegated and not task.is_closed() and self.is_proved(task)

    def checkable_ids(self, tasks: list[Task]) -> list[int]:
        return [task.id for task in tasks if self.is_checkable(task)]

    def short_proofs(self, task: Task) -> list[Proof]:
        return [proof for proof in self.children(task) if proof.state == ProofState.SHORT]

    def changed_point_proofs(self, task: Task, points: tuple[int, ...]) -> list[Proof]:
        return [proof for proof in self.children(task) if proof.point in points]

    def point_proofs(self, task: Task, point: int) -> list[Proof]:
        return sorted((proof for proof in self.children(task) if proof.point == point), key=lambda proof: proof.row_id)
