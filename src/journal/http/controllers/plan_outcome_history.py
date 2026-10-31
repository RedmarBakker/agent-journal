import json

from journal.http.support.download_response import DownloadResponse
from journal.http.support.request import Request
from journal.repositories.delivery_forecasts import DeliveryForecasts
from journal.repositories.plan_outcome_history import PlanOutcomeHistory
from journal.features.estimates.support.work_in_progress import WorkInProgress
from journal.support.response import Response


class PlanOutcomeHistoryController:
    """The plan owner's JSON read and downloadable copy of the same outcome history."""

    def __init__(self, history: PlanOutcomeHistory, forecasts: DeliveryForecasts, flow: WorkInProgress) -> None:
        self.history, self.forecasts, self.flow = history, forecasts, flow

    def show(self, request: Request) -> Response:
        return Response.json(self.history.read(request.number("id"), request.actor))

    def export(self, request: Request) -> DownloadResponse:
        plan_id = request.number("id")
        content = json.dumps(self.history.read(plan_id, request.actor), sort_keys=True, indent=2).encode("utf-8")
        return DownloadResponse("application/json; charset=utf-8", content, name=f"plan-{plan_id}-outcomes.json")

    def forecast(self, request: Request) -> Response:
        plan_id = request.number("id")
        return Response.json({**self.forecasts.plan(plan_id, request.actor), **self.flow.plan(plan_id)})
