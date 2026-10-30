from journal.events.listener import Listener
from journal.events.moments.worker_work_merged import WorkerWorkMerged
from journal.repositories.delivery_records import DeliveryRecords


class MergedDeliveryEvidence(Listener[WorkerWorkMerged]):
    """A checked worker merge is the trusted evidence origin for domains whose done policy accepts verified output."""

    def __init__(self, records: DeliveryRecords) -> None:
        self.records = records

    def handle(self, event: WorkerWorkMerged) -> None:
        self.records.merged(event)
