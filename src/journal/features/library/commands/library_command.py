from argparse import Namespace

from journal.console.command import Command
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_connect import LibraryConnect
from journal.support.caller import Caller
from journal.support.rejection import Rejection
from journal.sync.team_url import TeamUrl

PASSWORD_MISSING = "the password is asked by the journal command itself, unseen, in a terminal: run this line yourself in your own terminal, not through the agent"


class LibraryCommand(Command):
    """The team's library: connect this journal to it by URL, see how it stands, log in again, and disconnect."""

    noun = "library"

    def __init__(self, account: LibraryAccount, connect: LibraryConnect) -> None:
        self.account, self.connect_step = account, connect

    def arguments(self, verbs) -> None:
        connect = self.verb(verbs, "connect", "connect to a team's library by its URL: a new server's bare URL makes you its admin, an invitation URL an admin shared makes you a member, a bare URL with your account logs you in")
        connect.add_argument("url", help="the library server's URL, or the invitation URL an admin shared")
        connect.add_argument("--email", required=True, help="your email, the account's user name")
        connect.add_argument("--name", default="", help="the name the team sees beside what you publish")
        connect.add_argument("--password", default="", help="filled in by the journal command's own prompt; never type it on a command line")
        login = self.verb(verbs, "login", "log this machine in again, as after its device was revoked")
        login.add_argument("--email", required=True)
        login.add_argument("--password", default="", help="filled in by the journal command's own prompt; never type it on a command line")
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
