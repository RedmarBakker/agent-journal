from argparse import Namespace

from journal.console.command import Command
from journal.db.schema import Schema
from journal.features.library.support.library_accounts import LibraryAccounts
from journal.features.library.support.library_connect import LibraryConnect
from journal.features.library.support.library_link import LibraryLink
from journal.features.library.support.team_verb import TeamVerb
from journal.support.caller import Caller
from journal.support.rejection import Rejection
from journal.sync.team_url import TeamUrl

PASSWORD_MISSING = "the password is asked by the journal command itself, unseen, in a terminal: run this line yourself in your own terminal, not through the agent"


class TeamCommand(Command):
    """The team this journal is connected to: connect by URL, see how it stands, log in again, disconnect, and the admin's invitations, people and devices."""

    noun = "team"

    def __init__(self, accounts: LibraryAccounts, connect: LibraryConnect, schema: Schema) -> None:
        self.accounts, self.connect_step, self.schema = accounts, connect, schema

    def arguments(self, verbs) -> None:
        connect = self.verb(verbs, "connect", "connect to a team's server by its URL: a new server's bare URL makes you its admin, an invitation URL an admin shared makes you a member, a bare URL with your account logs you in")
        connect.add_argument("url", help="the team server's URL, or the invitation URL an admin shared")
        connect.add_argument("--email", required=True, help="your email, the account's user name")
        connect.add_argument("--name", default="", help="the name the team sees beside what you publish")
        connect.add_argument("--password", default="", help="filled in by the journal command's own prompt; never type it on a command line")
        connect.add_argument("--team", default="", help="the team's name in this journal; its host when left out")
        login = TeamVerb.added(self.verb(verbs, "login", "log this machine in again, as after its device was revoked"))
        login.add_argument("--email", required=True)
        login.add_argument("--password", default="", help="filled in by the journal command's own prompt; never type it on a command line")
        TeamVerb.added(self.verb(verbs, "invite", "an invitation URL for a person's email; admins only")).add_argument("email")
        TeamVerb.added(self.verb(verbs, "devices", "every device of the team's people; admins only"))
        TeamVerb.added(self.verb(verbs, "revoke", "revoke a device, which then needs journal team login; admins only")).add_argument("device", type=int)
        TeamVerb.added(self.verb(verbs, "people", "the team's people and their roles"))
        TeamVerb.added(self.verb(verbs, "remove", "remove a person from the team; admins only")).add_argument("account", type=int)
        TeamVerb.added(self.verb(verbs, "reset", "a new password for a person, to hand to them; admins only")).add_argument("account", type=int)
        changing = TeamVerb.added(self.verb(verbs, "password", "change your own password"))
        changing.add_argument("--old", required=True)
        changing.add_argument("--new", required=True)
        self.verb(verbs, "status", "the teams this journal is connected to, as whom and in which role; one team with --team").add_argument("--team", default="", help="the one team to show")
        TeamVerb.added(self.verb(verbs, "disconnect", "disconnect from one team; the others stay connected, and what you imported from its library stays"))

    def connect(self, args: Namespace, caller: Caller) -> int:
        connection = self.connect_step.connected(TeamUrl.parse(args.url), args.email, args.name or args.email.split("@")[0], self.typed_password(args), args.team)
        print(f"connected to the team at {connection.address} as {connection.name}, {connection.role}")
        return 0

    def login(self, args: Namespace, caller: Caller) -> int:
        connection = self.connect_step.renewed_connection(self.accounts.chosen(args.team), args.email, self.typed_password(args))
        print(f"logged in again to the team at {connection.address} as {connection.name}")
        return 0

    def invite(self, args: Namespace, caller: Caller) -> int:
        answer = self.link(args).invite(args.email)
        print(f"{answer.email} connects with this URL until {answer.expires_at:.0f}:\n\n    {self.accounts.chosen(args.team).invitation_url(answer.code)}")
        return 0

    def devices(self, args: Namespace, caller: Caller) -> int:
        for device in self.link(args).devices().devices:
            print(f"{device.id:<5} {device.name:<30} user {device.account_id}{'  revoked' if device.is_revoked() else ''}")
        return 0

    def revoke(self, args: Namespace, caller: Caller) -> int:
        device = self.link(args).revoke(args.device)
        print(f"device {device.id}, {device.name}, is revoked")
        return 0

    def people(self, args: Namespace, caller: Caller) -> int:
        for person in self.link(args).people().people:
            print(f"{person.id:<5} {person.name:<30} {person.role}")
        return 0

    def remove(self, args: Namespace, caller: Caller) -> int:
        print(f"{self.link(args).remove_person(args.account)} is removed from the team")
        return 0

    def reset(self, args: Namespace, caller: Caller) -> int:
        print(f"the new password of account {args.account}, to hand to them: {self.link(args).reset_password(args.account)}")
        return 0

    def password(self, args: Namespace, caller: Caller) -> int:
        self.link(args).change_password(args.old, args.new)
        print("your password is changed")
        return 0

    def status(self, args: Namespace, caller: Caller) -> int:
        accounts = [self.accounts.team(args.team)] if args.team else self.accounts.all()
        if not accounts:
            print("connected to no team: journal team connect <url> --email <you>")
        for account in accounts:
            connection = account.connection()
            print(f"team {connection.address}, as {connection.name} ({connection.role}), device {connection.device_id}, called {connection.team} here")
        return 0

    def disconnect(self, args: Namespace, caller: Caller) -> int:
        print(f"disconnected from the team at {self.accounts.chosen(args.team).disconnect()}; what you imported from its library stays")
        return 0

    def link(self, args: Namespace) -> LibraryLink:
        return LibraryLink(self.accounts.chosen(args.team), self.schema)

    @staticmethod
    def typed_password(args: Namespace) -> str:
        if not args.password:
            raise Rejection(PASSWORD_MISSING)
        return args.password
