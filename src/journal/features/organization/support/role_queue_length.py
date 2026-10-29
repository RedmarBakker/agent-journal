from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.links import Links
from journal.repositories.tasks import QUEUED_LINK


class RoleQueueLength:
    """How many tasks wait in the queues of a Role's running instances; the one place the viewer's queue figures come from, so another way of queuing on a Role changes it here alone."""

    def __init__(self, links: Links) -> None:
        self.links = links

    def items(self, instances: list[Worker]) -> tuple[tuple[Worker, Ref], ...]:
        return tuple((worker, task) for worker in instances for task in self.links.targets(worker, QUEUED_LINK))

    def queued_for(self, tasks: list[Task]) -> tuple[tuple[Ref, Ref], ...]:
        return tuple((link.source, link.target) for link in self.links.ref_links("target", [Ref.build(task) for task in tasks], QUEUED_LINK))

    def of(self, instances: list[Worker]) -> int:
        return len(self.items(instances))
