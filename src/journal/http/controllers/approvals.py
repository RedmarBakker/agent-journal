from journal.db.query import Query
from journal.features.organization.support.role_approvals import RoleApprovals
from journal.http.controllers.controller import Controller
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.models.approval import Approval
from journal.repositories.approvals import Approvals
from journal.support.response import Response
from journal.support.time_source import TimeSource


class ApprovalController(Controller[Approval]):
    """The Role actions waiting for the user and the decisions that let one through or refuse it."""

    repository: Approvals

    def __init__(self, approvals: Approvals, actions: RoleApprovals, time_source: TimeSource) -> None:
        self.repository, self.actions, self.time_source = approvals, actions, time_source

    def open_rows(self, query: Query) -> Query:
        return query.filter(decision=Approval.PENDING).filter_greater("expires_at", self.time_source.moment())

    def closed_rows(self, query: Query) -> Query:
        return query.filter_alternatives(query.filter_unequal("decision", Approval.PENDING), query.filter_less_equal("expires_at", self.time_source.moment()))

    def index_page(self, rows: list[Approval]) -> list[dict]:
        return self.shown_page(rows)

    def shown_page(self, rows: list[Approval]) -> list[dict]:
        return [ModelFields.build(row) for row in rows]

    def approve(self, request: Request) -> Response:
        approval = self.actions.approve(self.repository.find(request.number("id")), request.actor)
        return Response.json(self.shown(approval))

    def refuse(self, request: Request) -> Response:
        approval = self.actions.refuse(self.repository.find(request.number("id")), request.actor)
        return Response.json(self.shown(approval))
