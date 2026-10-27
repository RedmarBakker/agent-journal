from dataclasses import asdict

from journal.db.schema import Schema
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_import import LibraryImport
from journal.features.library.support.library_connect import LibraryConnect
from journal.sync.team_url import TeamUrl
from journal.features.library.support.library_link import LibraryLink
from journal.features.library.support.library_publish import LibraryPublish
from journal.features.library.support.library_update import LibraryUpdate
from journal.http.support.request import Request
from journal.support.rejection import Rejection
from journal.repositories.library_items import LibraryItems
from journal.support.response import Response
from sync_server.item_query import ItemQuery


class LibraryController:
    """The team's library as the viewer reads and changes it, through the very support classes the library command uses: connecting and disconnecting, whether and to whom this journal is connected, the admin's invitations, devices, people and a password change, the items with the version imported of each, one item's versions, and importing, updating and publishing an item."""

    def __init__(self, account: LibraryAccount, schema: Schema, items: LibraryItems, importing: LibraryImport, updating: LibraryUpdate, publishing: LibraryPublish, connecting: LibraryConnect) -> None:
        self.account, self.schema, self.items = account, schema, items
        self.importing, self.updating, self.publishing, self.connecting = importing, updating, publishing, connecting

    def status(self, request: Request) -> Response:
        if not self.account.is_connected():
            return Response.json({"connected": False})
        return Response.json({"connected": True, **self.account.connection().fields(), "token": ""})

    def connect(self, request: Request) -> Response:
        url, email, password = (str(request.body.get(field, "")).strip() for field in ("url", "email", "password"))
        if not (url and email and password):
            raise Rejection("connecting to a library takes its address or invitation URL, your email and your password")
        connection = self.connecting.connected(TeamUrl.parse(url), email, str(request.body.get("name") or email.split("@")[0]), password)
        return Response.json({"connected": True, **connection.fields(), "token": ""})

    def disconnect(self, request: Request) -> Response:
        return Response.json({"connected": False, "address": self.account.disconnect()})

    def invite(self, request: Request) -> Response:
        answer = LibraryLink(self.account, self.schema).invite(str(request.body.get("email", "")))
        return Response.json({"email": answer.email, "url": self.account.invitation_url(answer.code), "expires_at": answer.expires_at})

    def devices(self, request: Request) -> Response:
        return Response.json({"devices": [asdict(device) for device in LibraryLink(self.account, self.schema).devices().devices]})

    def revoke(self, request: Request) -> Response:
        return Response.json(asdict(LibraryLink(self.account, self.schema).revoke(int(request.body.get("device", 0)))))

    def people(self, request: Request) -> Response:
        return Response.json({"people": [asdict(person) for person in LibraryLink(self.account, self.schema).people().people]})

    def password(self, request: Request) -> Response:
        LibraryLink(self.account, self.schema).change_password(str(request.body.get("old", "")), str(request.body.get("new", "")))
        return Response.json({"changed": True})

    def items_listed(self, request: Request) -> Response:
        entries = LibraryLink(self.account, self.schema).items(ItemQuery(request.query.get("type"), request.query.get("search"))).items
        key = self.account.connection().key
        return Response.json({"items": [{**asdict(entry), "imported_version": self.imported_version(key, entry.item.item_type, entry.item.name)} for entry in entries]})

    def item(self, request: Request) -> Response:
        answer = LibraryLink(self.account, self.schema).item(request.params["item_type"], request.params["name"])
        imported = self.imported_version(self.account.connection().key, answer.item.item_type, answer.item.name)
        return Response.json({**asdict(answer), "imported_version": imported})

    def import_item(self, request: Request) -> Response:
        item = self.importing.imported(request.params["item_type"], request.params["name"], request.body.get("version"), request.actor, bool(request.body.get("accept")))
        return Response.json({"item_type": item.item_type, "name": item.name, "version": item.version})

    def update_item(self, request: Request) -> Response:
        item = self.updating.updated(request.params["item_type"], request.params["name"], request.actor, bool(request.body.get("replace")))
        return Response.json({"item_type": item.item_type, "name": item.name, "version": item.version})

    def publish_item(self, request: Request) -> Response:
        if not request.body.get("reference"):
            raise Rejection("publishing takes the number of the sequence or template, or the name of the profile, as reference")
        version = self.publishing.published(request.params["item_type"], str(request.body["reference"]), str(request.body.get("note", "")), request.body.get("description"))
        return Response.json(asdict(version))

    def imported_version(self, key: str, item_type: str, name: str) -> int:
        imported = self.items.imported(key, item_type, name)
        return imported.version if imported is not None and self.items.has_copy(imported, self.account.config.root) else 0
