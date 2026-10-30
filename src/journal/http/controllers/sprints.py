from journal.http.support.request import Request
from journal.models.sprint_state import SprintState
from journal.repositories.delivery_forecasts import DeliveryForecasts
from journal.repositories.sprint_outcome_metrics import SprintOutcomeMetrics
from journal.repositories.sprints import Sprints
from journal.support.rejection import Rejection
from journal.support.response import Response


class SprintController:
    """The owner's fixed sprint periods, membership, frozen commitments and carry-over decisions."""

    def __init__(self, sprints: Sprints, metrics: SprintOutcomeMetrics, forecasts: DeliveryForecasts) -> None:
        self.sprints, self.metrics, self.forecasts = sprints, metrics, forecasts

    def index(self, request: Request) -> Response:
        return Response.json(self.sprints.index(request.actor))

    def show(self, request: Request) -> Response:
        return Response.json(self.sprints.show(request.number("id"), request.actor))

    def metrics_report(self, request: Request) -> Response:
        return Response.json(self.metrics.read(request.number("id"), request.actor))

    def forecast(self, request: Request) -> Response:
        return Response.json(self.forecasts.sprint(request.number("id"), request.actor))

    def store(self, request: Request) -> Response:
        sprint = self.sprints.create(self.text(request, "starts_on"), self.text(request, "timezone"), request.actor)
        return Response.json(self.sprints.show(sprint.row_id, request.actor), 201)

    def calendar(self, request: Request) -> Response:
        length = request.body.get("length_days")
        length_days = self.number(length, "length_days") if length is not None else None
        sprint = self.sprints.change_calendar(request.number("id"), self.text(request, "starts_on"), self.text(request, "timezone"), length_days, request.actor)
        return Response.json(self.sprints.show(sprint.row_id, request.actor))

    def assign(self, request: Request) -> Response:
        sprint = self.sprints.assign(request.number("id"), self.number(request.body.get("plan_id"), "plan_id"), str(request.body.get("reason", "")), request.actor)
        return Response.json(self.sprints.show(sprint.row_id, request.actor))

    def start(self, request: Request) -> Response:
        sprint = self.sprints.start(request.number("id"), request.actor)
        return Response.json(self.sprints.show(sprint.row_id, request.actor))

    def close(self, request: Request) -> Response:
        sprint_id = request.number("id")
        current = self.sprints.show(sprint_id, request.actor)
        if current["state"] == SprintState.CLOSED.value:
            return Response.json(current)
        retrospective = self.metrics.close_report(sprint_id, request.actor)
        self.sprints.close(sprint_id, retrospective, request.actor)
        return Response.json(self.sprints.show(sprint_id, request.actor))

    def carry(self, request: Request) -> Response:
        sprint_id = request.number("id")
        plan_id = self.number(request.body.get("plan_id"), "plan_id")
        task_ids = self.metrics.remaining_task_ids(sprint_id, plan_id, request.actor)
        sprint = self.sprints.carry(sprint_id, plan_id,
                                    self.number(request.body.get("next_sprint_id", 0), "next_sprint_id"),
                                    str(request.body.get("reason", "")), task_ids, request.actor)
        return Response.json(self.sprints.show(sprint.row_id, request.actor))

    @staticmethod
    def text(request: Request, name: str) -> str:
        value = request.body.get(name)
        if not isinstance(value, str) or not value.strip():
            raise Rejection(f"{name} is required")
        return value

    @staticmethod
    def number(value: object, name: str) -> int:
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        raise Rejection(f"{name} must be a row number")
