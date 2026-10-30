from dataclasses import asdict

from journal.db.schema import Schema
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_connect import LibraryConnect
from journal.features.library.support.library_link import LibraryLink
from journal.http.support.request import Request
from journal.support.rejection import Rejection
from journal.support.response import Response
from journal.sync.team_url import TeamUrl


class TeamController:
    """The team as the viewer reads and changes it, through the very support classes the team command uses: whether and to whom this journal is connected, connecting and disconnecting, the admin's invitations, devices and people, and a password change."""

    def __init__(self, account: LibraryAccount, schema: Schema, connecting: LibraryConnect) -> None:
        self.account, self.schema, self.connecting = account, schema, connecting

    def status(self, request: Request) -> Response:
        if not self.account.is_connected():
            return Response.json({"connected": False})
        return Response.json({"connected": True, **self.account.connection().fields(), "token": ""})

    def connect(self, request: Request) -> Response:
        url, email, password = (str(request.body.get(field, "")).strip() for field in ("url", "email", "password"))
        if not (url and email and password):
            raise Rejection("connecting to a team takes its server's address or invitation URL, your email and your password")
        connection = self.connecting.connected(TeamUrl.parse(url), email, str(request.body.get("name") or email.split("@")[0]), password)
        return Response.json({"connected": True, **connection.fields(), "token": ""})

    def disconnect(self, request: Request) -> Response:
        return Response.json({"connected": False, "address": self.account.disconnect()})

    def invite(self, request: Request) -> Response:
        answer = self.link().invite(str(request.body.get("email", "")))
        return Response.json({"email": answer.email, "url": self.account.invitation_url(answer.code), "expires_at": answer.expires_at})

    def devices(self, request: Request) -> Response:
        return Response.json({"devices": [asdict(device) for device in self.link().devices().devices]})

    def revoke(self, request: Request) -> Response:
        return Response.json(asdict(self.link().revoke(int(request.body.get("device", 0)))))

    def people(self, request: Request) -> Response:
        return Response.json({"people": [asdict(person) for person in self.link().people().people]})

    def password(self, request: Request) -> Response:
        self.link().change_password(str(request.body.get("old", "")), str(request.body.get("new", "")))
        return Response.json({"changed": True})

    def link(self) -> LibraryLink:
        return LibraryLink(self.account, self.schema)
