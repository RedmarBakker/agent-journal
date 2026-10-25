from journal.db.query import Query
from journal.features.sharing.share_actions import ShareActions
from journal.features.sharing.share_targets import ShareTargets
from journal.features.sharing.support.tunnel import Tunnel
from journal.http.controllers.controller import Controller
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.share import Share
from journal.repositories.shares import Shares


class ShareController(Controller[Share]):
    """The links that let someone outside read one document, report or plan: each with whether it asks for a password, never the password, and one read by id with its address and what it opens."""

    repository: Shares

    def __init__(self, shares: Shares, actions: ShareActions, targets: ShareTargets, tunnel: Tunnel) -> None:
        self.repository, self.actions, self.targets, self.tunnel = shares, actions, targets, tunnel

    def open_rows(self, query: Query) -> Query:
        return query.filter_null("stopped_at")

    def closed_rows(self, query: Query) -> Query:
        return query.filter_present("stopped_at")

    def index_page(self, rows: list[Share]) -> list[dict]:
        return [self.public_fields(share) for share in rows]

    def shown_page(self, rows: list[Share]) -> list[dict]:
        return [self.described(share) for share in rows]

    def public_fields(self, share: Share) -> dict:
        return {**{name: value for name, value in ModelFields.build(share).items() if name != "password"}, "locked": bool(share.password)}

    def described(self, share: Share) -> dict:
        target = self.targets.targets(share)
        return {**self.public_fields(share), "link": self.tunnel.share_link(share.token), "target": str(target) if target else "", "opens": self.targets.opens(str(target)) if target else []}

    def store(self, request: Request) -> Response:
        body = request.body
        share = self.actions.create(str(body.get("target", "")), str(body.get("expires", "7d")), str(body.get("password", "")), bool(body.get("comments")), request.actor)
        return Response.json(self.shown(share), 201)

    def approve(self, request: Request) -> Response:
        return Response.json(self.shown(self.actions.approve(self.repository.find(request.number("id")), request.actor)))

    def stop(self, request: Request) -> Response:
        return Response.json(self.shown(self.actions.stop(self.repository.find(request.number("id")), request.actor)))

    def opens(self, request: Request) -> Response:
        return Response.json(self.targets.opens(request.query.get("target", "")))
