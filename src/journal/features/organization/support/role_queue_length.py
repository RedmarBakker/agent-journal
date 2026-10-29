from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.links import Links
from journal.repositories.tasks import QUEUED_LINK


class RoleQueueLength:
    """How many tasks wait in the queues of a Role's running instances; the one place the viewer's queue figures come from, so another way of queuing on a Role changes it here alone."""

    def __init__(self, links: Links) -> None:
        self.links = links

    def of(self, instances: list[Worker]) -> int:
        return sum(len(self.links.all_matching(source=Ref.build(worker), link_type=QUEUED_LINK)) for worker in instances)
