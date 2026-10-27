from argparse import Namespace

from journal.console.command import Command
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_connect import LibraryConnect
from journal.features.library.support.library_publish import LibraryPublish
from journal.features.library.support.library_import import LibraryImport
from journal.features.library.support.library_update import LibraryUpdate
from journal.features.library.support.library_link import LibraryLink
from journal.repositories.library_items import LibraryItems
from journal.db.schema import Schema
from sync_server.item_query import ItemQuery
from journal.support.caller import Caller
from journal.support.rejection import Rejection
from journal.sync.team_url import TeamUrl

PASSWORD_MISSING = "the password is asked by the journal command itself, unseen, in a terminal: run this line yourself in your own terminal, not through the agent"


class LibraryCommand(Command):
    """The team's library: connect this journal to it by URL, see how it stands, log in again, and disconnect."""

    noun = "library"

    def __init__(self, account: LibraryAccount, connect: LibraryConnect, publishing: LibraryPublish, items: LibraryItems, schema: Schema, importing: LibraryImport, updating: LibraryUpdate) -> None:
        self.account, self.connect_step, self.publishing, self.items, self.schema, self.importing = account, connect, publishing, items, schema, importing
        self.updating = updating

    def arguments(self, verbs) -> None:
        connect = self.verb(verbs, "connect", "connect to a team's library by its URL: a new server's bare URL makes you its admin, an invitation URL an admin shared makes you a member, a bare URL with your account logs you in")
        connect.add_argument("url", help="the library server's URL, or the invitation URL an admin shared")
        connect.add_argument("--email", required=True, help="your email, the account's user name")
        connect.add_argument("--name", default="", help="the name the team sees beside what you publish")
        connect.add_argument("--password", default="", help="filled in by the journal command's own prompt; never type it on a command line")
        login = self.verb(verbs, "login", "log this machine in again, as after its device was revoked")
        login.add_argument("--email", required=True)
        login.add_argument("--password", default="", help="filled in by the journal command's own prompt; never type it on a command line")
        publish = self.verb(verbs, "publish", "publish a sequence or template by its number, or a profile by its name, as the next version of it in the library")
        publish.add_argument("item_type", choices=("sequence", "template", "profile"))
        publish.add_argument("reference", help="the sequence's or template's number, or the profile's name")
        publish.add_argument("--note", default="", help="what this version changes, for whoever imports it")
        publish.add_argument("--description", default=None, help="what the item is for; its title when left out")
        listing = self.verb(verbs, "list", "the library's items with their latest version, and the version you imported of each")
        listing.add_argument("item_type", nargs="?", default=None, help="one type of item: sequence, template, profile, reader, skill, document, file or plan")
        listing.add_argument("--search", default=None, help="words to find in the item's name or description")
        item_parser = self.verb(verbs, "show", "one item of the library: what it is for, every version with its note, and the version you have")
        item_parser.add_argument("item_type")
        item_parser.add_argument("name")
        importing = self.verb(verbs, "import", "import an item of the library into this journal: the latest version, or the one --version gives")
        importing.add_argument("item_type", choices=("sequence", "template", "profile"))
        importing.add_argument("name")
        importing.add_argument("--version", type=int, default=None)
        importing.add_argument("--accept", action="store_true", help="write a sequence whose triggers and allowed commands you have read")
        updating = self.verb(verbs, "update", "bring an imported item to the library's latest version; an item edited here is refused unless --replace")
        updating.add_argument("item_type", choices=("sequence", "template", "profile"))
        updating.add_argument("name")
        updating.add_argument("--replace", action="store_true", help="take the latest version over your edits")
        withdrawing = self.verb(verbs, "withdraw", "take an item off the library's list; its versions stay readable to whoever imported them")
        withdrawing.add_argument("item_type")
        withdrawing.add_argument("name")
        deleting = self.verb(verbs, "delete", "delete one version of an item for good, as one published with a secret in it; admins only")
        deleting.add_argument("item_type")
        deleting.add_argument("name")
        deleting.add_argument("number", type=int)
        self.verb(verbs, "invite", "an invitation URL for a person's email; admins only").add_argument("email")
        self.verb(verbs, "devices", "every device of the library's people; admins only")
        self.verb(verbs, "revoke", "revoke a device, which then needs journal library login; admins only").add_argument("device", type=int)
        self.verb(verbs, "people", "the library's people and their roles")
        self.verb(verbs, "remove", "remove a person from the library; admins only").add_argument("account", type=int)
        self.verb(verbs, "reset", "a new password for a person, to hand to them; admins only").add_argument("account", type=int)
        changing = self.verb(verbs, "password", "change your own password")
        changing.add_argument("--old", required=True)
        changing.add_argument("--new", required=True)
        self.verb(verbs, "status", "the library this journal is connected to, as whom and in which role")
        self.verb(verbs, "disconnect", "disconnect from the library; what you imported stays")

    def connect(self, args: Namespace, caller: Caller) -> int:
        connection = self.connect_step.connected(TeamUrl.parse(args.url), args.email, args.name or args.email.split("@")[0], self.password(args))
        print(f"connected to the library at {connection.address} as {connection.name}, {connection.role}")
        return 0

    def login(self, args: Namespace, caller: Caller) -> int:
        connection = self.connect_step.renewed_connection(args.email, self.password(args))
        print(f"logged in again to the library at {connection.address} as {connection.name}")
        return 0

    def publish(self, args: Namespace, caller: Caller) -> int:
        version = self.publishing.published(args.item_type, args.reference, args.note, args.description)
        print(f"published {args.item_type} {args.reference} as version {version.number} of the library's item")
        return 0

    def import_(self, args: Namespace, caller: Caller) -> int:
        item = self.importing.imported(args.item_type, args.name, args.version, caller.actor, args.accept)
        print(f"imported {item.item_type} {item.name}, version {item.version}" + (f", written to {item.file_path}" if item.file_path else ""))
        return 0

    def update(self, args: Namespace, caller: Caller) -> int:
        item = self.updating.updated(args.item_type, args.name, caller.actor, args.replace)
        print(f"{item.item_type} {item.name} is now at version {item.version}")
        return 0

    def withdraw(self, args: Namespace, caller: Caller) -> int:
        self.link().withdraw(args.item_type, args.name)
        print(f"{args.item_type} {args.name} is off the library's list; its versions stay readable")
        return 0

    def delete(self, args: Namespace, caller: Caller) -> int:
        version = self.link().delete_version(args.item_type, args.name, args.number)
        print(f"version {version.number} of {args.item_type} {args.name} is deleted for good")
        return 0

    def invite(self, args: Namespace, caller: Caller) -> int:
        answer = self.link().invite(args.email)
        print(f"{answer.email} connects with this URL until {answer.expires_at:.0f}:\n\n    {self.account.invitation_url(answer.code)}")
        return 0

    def devices(self, args: Namespace, caller: Caller) -> int:
        for device in self.link().devices().devices:
            print(f"{device.id:<5} {device.name:<30} user {device.account_id}{'  revoked' if device.is_revoked() else ''}")
        return 0

    def revoke(self, args: Namespace, caller: Caller) -> int:
        device = self.link().revoke(args.device)
        print(f"device {device.id}, {device.name}, is revoked")
        return 0

    def people(self, args: Namespace, caller: Caller) -> int:
        for person in self.link().people().people:
            print(f"{person.id:<5} {person.name:<30} {person.role}")
        return 0

    def remove(self, args: Namespace, caller: Caller) -> int:
        print(f"{self.link().remove_person(args.account)} is removed from the library")
        return 0

    def reset(self, args: Namespace, caller: Caller) -> int:
        print(f"the new password of account {args.account}, to hand to them: {self.link().reset_password(args.account)}")
        return 0

    def password(self, args: Namespace, caller: Caller) -> int:
        self.link().change_password(args.old, args.new)
        print("your password is changed")
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        entries = self.link().items(ItemQuery(args.item_type, args.search)).items
        if not entries:
            print("no items in the library" + (f" of type {args.item_type}" if args.item_type else ""))
        for entry in entries:
            print(f"{entry.item.item_type} {entry.item.name}: version {entry.version.number}{self.imported_note(entry.item.item_type, entry.item.name)}, {entry.item.description}")
        return 0

    def show(self, args: Namespace, caller: Caller) -> int:
        answer = self.link().item(args.item_type, args.name)
        print(f"{answer.item.item_type} {answer.item.name}{self.imported_note(answer.item.item_type, answer.item.name)}: {answer.item.description}")
        for version in answer.versions:
            print(f"  version {version.number}, needs journal {version.lowest_version}: {version.note or 'no note'}")
        return 0

    def imported_note(self, item_type: str, name: str) -> str:
        imported = self.items.imported(self.account.connection().key, item_type, name)
        if imported is None or not self.items.has_copy(imported, self.account.config.root):
            return ""
        return f", you have {imported.version}"

    def link(self) -> LibraryLink:
        return LibraryLink(self.account, self.schema)

    def status(self, args: Namespace, caller: Caller) -> int:
        if not self.account.is_connected():
            print("connected to no library: journal library connect <url> --email <you>")
            return 0
        connection = self.account.connection()
        print(f"library {connection.address}, as {connection.name} ({connection.role}), device {connection.device_id}")
        return 0

    def disconnect(self, args: Namespace, caller: Caller) -> int:
        print(f"disconnected from the library at {self.account.disconnect()}; what you imported stays")
        return 0

    @staticmethod
    def password(args: Namespace) -> str:
        if not args.password:
            raise Rejection(PASSWORD_MISSING)
        return args.password
