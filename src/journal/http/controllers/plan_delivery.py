from journal.http.support.request import Request
from journal.repositories.delivery_records import DeliveryRecords
from journal.support.response import Response


class PlanDeliveryController:
    """The read projection and actor-checked evidence operation for a plan's domain delivery."""

    def __init__(self, records: DeliveryRecords) -> None:
        self.records = records

    def show(self, request: Request) -> Response:
        return Response.json(self.records.show(request.number("id")))

    def record(self, request: Request) -> Response:
        return Response.json(self.records.record(request.number("id"), request.body, request.actor))
