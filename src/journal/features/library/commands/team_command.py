from argparse import Namespace

from journal.console.command import Command
from journal.db.schema import Schema
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_connect import LibraryConnect
from journal.features.library.support.library_link import LibraryLink
from journal.support.caller import Caller
from journal.support.rejection import Rejection
from journal.sync.team_url import TeamUrl

PASSWORD_MISSING = "the password is asked by the journal command itself, unseen, in a terminal: run this line yourself in your own terminal, not through the agent"


class TeamCommand(Command):
    """The team this journal is connected to: connect by URL, see how it stands, log in again, disconnect, and the admin's invitations, people and devices."""

    noun = "team"

    def __init__(self, account: LibraryAccount, connect: LibraryConnect, schema: Schema) -> None:
        self.account, self.connect_step, self.schema = account, connect, schema

    def arguments(self, verbs) -> None:
        connect = self.verb(verbs, "connect", "connect to a team's server by its URL: a new server's bare URL makes you its admin, an invitation URL an admin shared makes you a member, a bare URL with your account logs you in")
        connect.add_argument("url", help="the team server's URL, or the invitation URL an admin shared")
        connect.add_argument("--email", required=True, help="your email, the account's user name")
        connect.add_argument("--name", default="", help="the name the team sees beside what you publish")
        connect.add_argument("--password", default="", help="filled in by the journal command's own prompt; never type it on a command line")
        login = self.verb(verbs, "login", "log this machine in again, as after its device was revoked")
        login.add_argument("--email", required=True)
        login.add_argument("--password", default="", help="filled in by the journal command's own prompt; never type it on a command line")
        self.verb(verbs, "invite", "an invitation URL for a person's email; admins only").add_argument("email")
        self.verb(verbs, "devices", "every device of the team's people; admins only")
        self.verb(verbs, "revoke", "revoke a device, which then needs journal team login; admins only").add_argument("device", type=int)
        self.verb(verbs, "people", "the team's people and their roles")
        self.verb(verbs, "remove", "remove a person from the team; admins only").add_argument("account", type=int)
        self.verb(verbs, "reset", "a new password for a person, to hand to them; admins only").add_argument("account", type=int)
        changing = self.verb(verbs, "password", "change your own password")
        changing.add_argument("--old", required=True)
        changing.add_argument("--new", required=True)
        self.verb(verbs, "status", "the team this journal is connected to, as whom and in which role")
        self.verb(verbs, "disconnect", "disconnect from the team; what you imported from its library stays")

    def connect(self, args: Namespace, caller: Caller) -> int:
        connection = self.connect_step.connected(TeamUrl.parse(args.url), args.email, args.name or args.email.split("@")[0], self.typed_password(args))
        print(f"connected to the team at {connection.address} as {connection.name}, {connection.role}")
        return 0

    def login(self, args: Namespace, caller: Caller) -> int:
        connection = self.connect_step.renewed_connection(args.email, self.typed_password(args))
        print(f"logged in again to the team at {connection.address} as {connection.name}")
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
        print(f"{self.link().remove_person(args.account)} is removed from the team")
        return 0

    def reset(self, args: Namespace, caller: Caller) -> int:
        print(f"the new password of account {args.account}, to hand to them: {self.link().reset_password(args.account)}")
        return 0

    def password(self, args: Namespace, caller: Caller) -> int:
        self.link().change_password(args.old, args.new)
        print("your password is changed")
        return 0

    def status(self, args: Namespace, caller: Caller) -> int:
        if not self.account.is_connected():
            print("connected to no team: journal team connect <url> --email <you>")
            return 0
        connection = self.account.connection()
        print(f"team {connection.address}, as {connection.name} ({connection.role}), device {connection.device_id}")
        return 0

    def disconnect(self, args: Namespace, caller: Caller) -> int:
        print(f"disconnected from the team at {self.account.disconnect()}; what you imported from its library stays")
        return 0

    def link(self) -> LibraryLink:
        return LibraryLink(self.account, self.schema)

    @staticmethod
    def typed_password(args: Namespace) -> str:
        if not args.password:
            raise Rejection(PASSWORD_MISSING)
        return args.password
