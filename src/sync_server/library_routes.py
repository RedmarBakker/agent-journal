from sync_server.item import Item
from sync_server.item_list_answer import ItemListAnswer
from sync_server.item_query import ItemQuery
from sync_server.item_version import ItemVersion
from sync_server.item_versions_answer import ItemVersionsAnswer
from sync_server.library_answer import LibraryAnswer
from sync_server.library_path import LibraryPath
from sync_server.protocol import PROTOCOL
from sync_server.publish_request import PublishRequest


class LibraryRoutes:
    """What each library route answers, the token checked on every one but GET /library, and none of them held to the team's version pin: the lowest journal version of a published version is the publisher's own, from its request's header."""

    def __init__(self, team) -> None:
        self.team = team

    def summary(self) -> LibraryAnswer:
        details = self.team.details.answer()
        return LibraryAnswer(details.name, details.key, PROTOCOL, details.has_admin, "")

    def member_summary(self, token: str) -> LibraryAnswer:
        return LibraryAnswer(**{**self.summary().__dict__, "role": self.team.devices.person(token).role})

    def listed(self, token: str, query: ItemQuery) -> ItemListAnswer:
        self.team.devices.device(token)
        return ItemListAnswer(self.team.library.listed(query.item_type, query.search))

    def item(self, token: str, path: LibraryPath) -> ItemVersionsAnswer:
        self.team.devices.device(token)
        item = self.team.library.item(path.item_type, path.name)
        return ItemVersionsAnswer(item, self.team.library.complete_versions(item))

    def version(self, token: str, path: LibraryPath) -> ItemVersion:
        self.team.devices.device(token)
        return self.team.library.numbered_version(path.item_type, path.name, path.number)

    def published(self, token: str, path: LibraryPath, request: PublishRequest, lowest_version: str) -> ItemVersion:
        return self.team.library.publish(self.team.devices.person(token), path.item_type, path.name, request.description, request.body, lowest_version, request.note, self.team.clock.time())

    def deleted(self, token: str, path: LibraryPath) -> ItemVersion:
        return self.team.library.version_deleted(self.team.devices.person(token), path.item_type, path.name, path.number)

    def withdrawn(self, token: str, path: LibraryPath) -> Item:
        return self.team.library.withdraw(self.team.devices.person(token), path.item_type, path.name, self.team.clock.time())

    def file_received(self, token: str, path: LibraryPath, data: bytes) -> ItemVersion:
        return self.team.library.file_received(self.team.devices.person(token), path.item_type, path.name, path.number, path.file_name, data, self.team.clock.time())

    def file(self, token: str, path: LibraryPath) -> bytes:
        self.team.devices.device(token)
        return self.team.library.item_file(path.item_type, path.name, path.number, path.file_name)
