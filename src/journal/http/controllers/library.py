from dataclasses import asdict

from journal.db.schema import Schema
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_import import LibraryImport
from journal.features.library.support.library_link import LibraryLink
from journal.features.library.support.library_publish import LibraryPublish
from journal.features.library.support.library_copy import LibraryCopy
from journal.features.library.support.library_update import LibraryUpdate
from journal.http.support.request import Request
from journal.support.rejection import Rejection
from journal.repositories.library_items import LibraryItems
from journal.support.response import Response
from sync_server.item_query import ItemQuery


class LibraryController:
    """The team's library as the viewer reads and changes it, through the very support classes the library command uses: the items with the version imported of each, one item's versions with the fields edited in the copy here, every copy here with the version it came from, and importing, updating and publishing an item."""

    def __init__(self, account: LibraryAccount, schema: Schema, items: LibraryItems, importing: LibraryImport, updating: LibraryUpdate, publishing: LibraryPublish) -> None:
        self.account, self.schema, self.items = account, schema, items
        self.importing, self.updating, self.publishing = importing, updating, publishing

    def items_listed(self, request: Request) -> Response:
        entries = LibraryLink(self.account, self.schema).items(ItemQuery(request.query.get("type"), request.query.get("search"))).items
        key = self.account.connection().key
        return Response.json({"items": [{**asdict(entry), "imported_version": self.imported_version(key, entry.item.item_type, entry.item.name)} for entry in entries]})

    def item(self, request: Request) -> Response:
        answer = LibraryLink(self.account, self.schema).item(request.params["item_type"], request.params["name"])
        imported = self.imported_version(self.account.connection().key, answer.item.item_type, answer.item.name)
        return Response.json({**asdict(answer), "imported_version": imported, "edited_fields": self.edited_fields(answer.item.item_type, answer.item.name) if imported else []})

    def edited_fields(self, item_type: str, name: str) -> list[str]:
        return self.updating.edited_fields(self.items.imported(self.account.connection().key, item_type, name))

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

    def copies(self, request: Request) -> Response:
        if not self.account.is_connected():
            return Response.json({"copies": []})
        items = self.items.library_rows(self.account.connection().key)
        return Response.json({"copies": [asdict(LibraryCopy.create(item, self.items.local_rows(item))) for item in items if self.items.has_copy(item, self.account.config.root)]})

    def imported_version(self, key: str, item_type: str, name: str) -> int:
        imported = self.items.imported(key, item_type, name)
        return imported.version if imported is not None and self.items.has_copy(imported, self.account.config.root) else 0
