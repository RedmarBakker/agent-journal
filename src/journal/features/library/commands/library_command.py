from argparse import REMAINDER, Namespace

from journal.console.command import Command
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_accounts import LibraryAccounts
from journal.features.library.support.team_verb import TeamVerb
from journal.features.library.support.library_publish import LibraryPublish
from journal.features.library.support.library_import import LibraryImport
from journal.features.library.support.library_update import LibraryUpdate
from journal.features.library.support.library_link import LibraryLink
from journal.repositories.library_items import LibraryItems
from journal.db.schema import Schema
from sync_server.item_query import ItemQuery
from journal.support.caller import Caller
from journal.support.rejection import Rejection

TEAM_CONNECTS = "the library is the team's: connect to the team with journal team connect <url> --email <you>"


class LibraryCommand(Command):
    """The team's library: publish, list, show, import, update, withdraw and delete its items."""

    noun = "library"

    def __init__(self, accounts: LibraryAccounts, publishing: LibraryPublish, items: LibraryItems, schema: Schema, importing: LibraryImport, updating: LibraryUpdate) -> None:
        self.accounts, self.publishing, self.items, self.schema, self.importing = accounts, publishing, items, schema, importing
        self.updating = updating

    def arguments(self, verbs) -> None:
        self.verb(verbs, "connect", "the library is the team's: connect with journal team connect").add_argument("words", nargs=REMAINDER)
        publish = TeamVerb.added(self.verb(verbs, "publish", "publish a sequence or template by its number, or a profile, reader or skill by its name, or a document or file by its path, as the next version of it in the library"))
        publish.add_argument("item_type", choices=("sequence", "template", "profile", "reader", "skill", "document", "file", "plan"))
        publish.add_argument("reference", help="the sequence's, template's or plan's number, or the profile's, reader's or skill's name, or the document's or file's path in the project")
        publish.add_argument("--note", default="", help="what this version changes, for whoever imports it")
        publish.add_argument("--description", default=None, help="what the item is for; its title when left out")
        listing = TeamVerb.added(self.verb(verbs, "list", "the library's items with their latest version, and the version you imported of each"))
        listing.add_argument("item_type", nargs="?", default=None, help="one type of item: sequence, template, profile, reader, skill, document, file or plan")
        listing.add_argument("--search", default=None, help="words to find in the item's name or description")
        item_parser = TeamVerb.added(self.verb(verbs, "show", "one item of the library: what it is for, every version with its note, and the version you have"))
        item_parser.add_argument("item_type")
        item_parser.add_argument("name")
        importing = TeamVerb.added(self.verb(verbs, "import", "import an item of the library into this journal: the latest version, or the one --version gives"))
        importing.add_argument("item_type", choices=("sequence", "template", "profile", "reader", "skill", "document", "file", "plan"))
        importing.add_argument("name")
        importing.add_argument("--version", type=int, default=None)
        importing.add_argument("--accept", action="store_true", help="write a sequence whose triggers and allowed commands, or a reader whose pattern or script, you have read")
        updating = TeamVerb.added(self.verb(verbs, "update", "bring an imported item to the library's latest version; an item edited here is refused unless --replace"))
        updating.add_argument("item_type", choices=("sequence", "template", "profile", "reader", "skill", "document", "file"))
        updating.add_argument("name")
        updating.add_argument("--replace", action="store_true", help="take the latest version over your edits")
        withdrawing = TeamVerb.added(self.verb(verbs, "withdraw", "take an item off the library's list; its versions stay readable to whoever imported them"))
        withdrawing.add_argument("item_type")
        withdrawing.add_argument("name")
        deleting = TeamVerb.added(self.verb(verbs, "delete", "delete one version of an item for good, as one published with a secret in it; admins only"))
        deleting.add_argument("item_type")
        deleting.add_argument("name")
        deleting.add_argument("number", type=int)

    def connect(self, args: Namespace, caller: Caller) -> int:
        raise Rejection(TEAM_CONNECTS)

    def publish(self, args: Namespace, caller: Caller) -> int:
        version = self.publishing.bound(self.team(args)).published(args.item_type, args.reference, args.note, args.description)
        print(f"published {args.item_type} {args.reference} as version {version.number} of the library's item")
        return 0

    def import_(self, args: Namespace, caller: Caller) -> int:
        item = self.importing.bound(self.team(args)).imported(args.item_type, args.name, args.version, caller.actor, args.accept)
        print(f"imported {item.item_type} {item.name}, version {item.version}" + (f", written to {item.file_path}" if item.file_path else ""))
        return 0

    def update(self, args: Namespace, caller: Caller) -> int:
        item = self.updating.bound(self.team(args)).updated(args.item_type, args.name, caller.actor, args.replace)
        print(f"{item.item_type} {item.name} is now at version {item.version}")
        return 0

    def withdraw(self, args: Namespace, caller: Caller) -> int:
        self.link(args).withdraw(args.item_type, args.name)
        print(f"{args.item_type} {args.name} is off the library's list; its versions stay readable")
        return 0

    def delete(self, args: Namespace, caller: Caller) -> int:
        version = self.link(args).delete_version(args.item_type, args.name, args.number)
        print(f"version {version.number} of {args.item_type} {args.name} is deleted for good")
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        entries = self.link(args).items(ItemQuery(args.item_type, args.search)).items
        if not entries:
            print("no items in the library" + (f" of type {args.item_type}" if args.item_type else ""))
        for entry in entries:
            print(f"{entry.item.item_type} {entry.item.name}: version {entry.version.number}{self.imported_note(args, entry.item.item_type, entry.item.name)}, {entry.item.description}")
        return 0

    def show(self, args: Namespace, caller: Caller) -> int:
        answer = self.link(args).item(args.item_type, args.name)
        print(f"{answer.item.item_type} {answer.item.name}{self.imported_note(args, answer.item.item_type, answer.item.name)}: {answer.item.description}")
        for version in answer.versions:
            print(f"  version {version.number}, needs journal {version.lowest_version}: {version.note or 'no note'}")
        return 0

    def imported_note(self, args: Namespace, item_type: str, name: str) -> str:
        imported = self.items.imported(self.team(args).connection().key, item_type, name)
        if imported is None or not self.items.has_copy(imported, self.accounts.config.root):
            return ""
        return f", you have {imported.version}"

    def link(self, args: Namespace) -> LibraryLink:
        return LibraryLink(self.team(args), self.schema)

    def team(self, args: Namespace) -> LibraryAccount:
        return self.accounts.chosen(args.team)
