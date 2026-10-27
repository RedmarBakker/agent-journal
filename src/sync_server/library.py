import hashlib
import re

from sync_server.account import Account
from sync_server.db.item_rows import ItemRows
from sync_server.db.item_version_rows import ItemVersionRows
from sync_server.db.store import Store
from sync_server.file_store import FileStore
from sync_server.item_file_place import ItemFilePlace
from sync_server.item import Item
from sync_server.item_version import ItemVersion
from sync_server.library_entry import LibraryEntry
from sync_server.missing_item import MissingItem
from sync_server.refusal import Refusal

# the kinds of item the library holds
ITEM_TYPES = ("sequence", "template", "profile", "reader", "skill", "document", "file", "plan")
# what a name may hold: letters, digits, and dot, dash or underscore between them
NAME_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,78}[A-Za-z0-9])?$")
# the most files one version names, and the most bytes its files hold together
VERSION_FILE_COUNT_LIMIT = 200
VERSION_BYTE_LIMIT = 200 * 1024 * 1024
# how long a version may wait for its files before the server clears it, its files and its number
INCOMPLETE_SECONDS = 24 * 3600


class Library:
    """The team's library of published items: a publish stores the next version of an item and never changes one already stored; a version waits for its files, the same publish sent again gets it back, and one left waiting a day is cleared with its files and its number; a new name is anyone's, a new version of a name only its first publisher's or an admin's; a withdrawn item leaves the list while its versions stay readable, and a new version of it lists it again."""

    def __init__(self, store: Store, items: ItemRows, versions: ItemVersionRows, files: FileStore) -> None:
        self.store, self.items, self.versions, self.files = store, items, versions, files

    def publish(self, account: Account, item_type: str, name: str, description: str, body: str, lowest_version: str, note: str, published_at: float) -> ItemVersion:
        self.check_name(item_type, name)
        body_hash = hashlib.sha256(body.encode()).hexdigest()
        with self.store.transaction():
            item = self.publishable(account, item_type, name, description, published_at)
            pending = self.pending_versions(item, published_at)
            resent = [version for version in pending if version.body_hash == body_hash and version.publisher_id == account.id]
            if resent:
                return resent[0]
            if len(ItemVersion.body_file_hashes(body)) > VERSION_FILE_COUNT_LIMIT:
                raise Refusal(f"a version names at most {VERSION_FILE_COUNT_LIMIT} files")
            number = self.versions.highest_number(item.id) + 1
            self.versions.insert(item.id, number, body, body_hash, lowest_version, note, account.id, published_at)
            version = ItemVersion.read(self.versions.numbered(item.id, number))
            return version if version.file_hashes() else self.completed(version, published_at)

    @staticmethod
    def check_name(item_type: str, name: str) -> None:
        if item_type not in ITEM_TYPES:
            raise Refusal(f"the library holds no {item_type}: it holds {', '.join(ITEM_TYPES)}")
        if not NAME_PATTERN.match(name):
            raise Refusal(f"{name!r} is no item name: letters and digits, with dot, dash or underscore between them, at most 80")

    def pending_versions(self, item: Item, checked_at: float) -> list[ItemVersion]:
        pending = [ItemVersion.read(row) for row in self.versions.incomplete(item.id)]
        for abandoned in [version for version in pending if checked_at - version.published_at >= INCOMPLETE_SECONDS]:
            self.versions.delete(abandoned.id)
            self.files.version_removed(item.item_type, item.name, abandoned.number)
        return [version for version in pending if checked_at - version.published_at < INCOMPLETE_SECONDS]

    def publishable(self, account: Account, item_type: str, name: str, description: str, published_at: float) -> Item:
        row = self.items.item_row(item_type, name)
        if row is None:
            return Item.read(self.items.numbered(self.items.insert(item_type, name, description, account.id, published_at)))
        item = Item.read(row)
        if not item.has_owner(account):
            raise Refusal(f"{item_type} {name} was published by someone else: only they or an admin publish a new version of it")
        if item.withdrawn_at:
            self.items.withdraw(item.id, 0)
        return item

    def file_received(self, account: Account, item_type: str, name: str, number: int, file_name: str, data: bytes, received_at: float) -> ItemVersion:
        with self.store.transaction():
            version = self.stored_version(item_type, name, number)
            if account.id != version.publisher_id:
                raise Refusal(f"{item_type} {name} version {number} takes files only from its publisher")
            expected = version.file_hashes().get(file_name)
            if expected is None:
                raise Refusal(f"{item_type} {name} version {number} names no file {file_name}")
            if hashlib.sha256(data).hexdigest() != expected:
                raise Refusal(f"{file_name} does not match the hash version {number} of {item_type} {name} names for it: send it again")
            if version.is_complete():
                return version
            if self.files.version_bytes(item_type, name, number) + len(data) > VERSION_BYTE_LIMIT:
                raise Refusal(f"version {number} of {item_type} {name} would hold more than {VERSION_BYTE_LIMIT // (1024 * 1024)} MB of files")
            self.files.put(ItemFilePlace(item_type, name, number, file_name), data)
            places = [ItemFilePlace(item_type, name, number, listed_file) for listed_file in version.file_hashes()]
            return self.completed(version, received_at) if all(self.files.is_stored(place) for place in places) else version

    def item_file(self, item_type: str, name: str, number: int, file_name: str) -> bytes:
        self.numbered_version(item_type, name, number)
        return self.files.get(ItemFilePlace(item_type, name, number, file_name))

    def completed(self, version: ItemVersion, completed_at: float) -> ItemVersion:
        self.versions.mark_complete(version.id, completed_at)
        return ItemVersion.read(self.versions.numbered(version.item_id, version.number))

    def listed(self, item_type: str | None, search: str | None) -> list[LibraryEntry]:
        items = [Item.read(row) for row in self.items.listed() if item_type in (None, row["item_type"]) and self.matches(row, search)]
        return [LibraryEntry(item, versions[-1]) for item in items if (versions := self.complete_versions(item))]

    def complete_versions(self, item: Item) -> list[ItemVersion]:
        return [ItemVersion.read(row) for row in self.versions.complete(item.id)]

    def item(self, item_type: str, name: str) -> Item:
        row = self.items.item_row(item_type, name)
        if row is None:
            raise MissingItem(f"no {item_type} named {name} in the library")
        return Item.read(row)

    def stored_version(self, item_type: str, name: str, number: int) -> ItemVersion:
        row = self.versions.numbered(self.item(item_type, name).id, number)
        if row is None:
            raise MissingItem(f"{item_type} {name} has no version {number}")
        return ItemVersion.read(row)

    def latest_version(self, item_type: str, name: str) -> ItemVersion:
        versions = self.complete_versions(self.item(item_type, name))
        if not versions:
            raise MissingItem(f"{item_type} {name} has no complete version yet")
        return versions[-1]

    def numbered_version(self, item_type: str, name: str, number: int) -> ItemVersion:
        matching = [version for version in self.complete_versions(self.item(item_type, name)) if version.number == number]
        if not matching:
            raise MissingItem(f"{item_type} {name} has no version {number}")
        return matching[0]

    def withdraw(self, account: Account, item_type: str, name: str, withdrawn_at: float) -> Item:
        item = self.item(item_type, name)
        if not item.has_owner(account):
            raise Refusal(f"{item_type} {name} was published by someone else: only they or an admin withdraw it")
        self.items.withdraw(item.id, withdrawn_at)
        return Item.read(self.items.numbered(item.id))

    @staticmethod
    def matches(row, search: str | None) -> bool:
        return search is None or search.lower() in f"{row['name']} {row['description']}".lower()
