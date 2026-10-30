import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from sync_server.accounts import Accounts
from sync_server.admin_handler import AdminHandler
from sync_server.db.invitation_rows import InvitationRows
from sync_server.invitations import Invitations
from sync_server.file_store import FileStore
from sync_server.db.account_rows import AccountRows
from sync_server.db.device_rows import DeviceRows
from sync_server.db.failed_login_rows import FailedLoginRows
from sync_server.db.server_schema import ServerSchema
from sync_server.db.store import Store
from sync_server.db.team_detail_rows import TeamDetailRows
from sync_server.team_details import TeamDetails
from sync_server.devices import Devices
from sync_server.login_handler import LoginHandler
from sync_server.people_handler import PeopleHandler
from sync_server.backup_handler import BackupHandler
from sync_server.server_backups import ServerBackups
from sync_server.item_file_place import ITEMS_FOLDER
from sync_server.server_clock import ServerClock
from sync_server.setup_code import SetupCode
from sync_server.team_request_handler import TeamRequestHandler
from sync_server.library import Library
from sync_server.library_routes import LibraryRoutes
from sync_server.db.item_rows import ItemRows
from sync_server.db.item_version_rows import ItemVersionRows

DATABASE = "team.db"
BACKUPS = "backups"
FILES = "files"


class TeamServer:
    """The team server put together over one database in its data folder: its accounts and devices and the library, and its threaded HTTP server."""

    def __init__(self, data: Path) -> None:
        self.store = Store(data / DATABASE)
        ServerSchema(self.store).migrated()
        self.clock = ServerClock()
        self.accounts = Accounts(AccountRows(self.store))
        self.details = TeamDetails(TeamDetailRows(self.store))
        self.devices = Devices(DeviceRows(self.store), FailedLoginRows(self.store), self.accounts)
        self.invitations = Invitations(self.store, InvitationRows(self.store), self.accounts)
        self.setup_code = SetupCode(data)
        self.logins = LoginHandler(self.devices, self.invitations, self.accounts, self.clock, self.setup_code)
        self.files = FileStore(data / FILES)
        self.library = Library(self.store, ItemRows(self.store), ItemVersionRows(self.store), self.files)
        self.library_routes = LibraryRoutes(self)
        self.admins = AdminHandler(self.devices, self.accounts, self.invitations, self.clock)
        self.people = PeopleHandler(self.accounts, self.devices)
        self.backups = ServerBackups(self.store, data / BACKUPS, data / FILES / ITEMS_FOLDER)
        self.backup_requests = BackupHandler(self.devices, self.backups)

    def http(self, host: str, port: int) -> ThreadingHTTPServer:
        server = ThreadingHTTPServer((host, port), TeamRequestHandler)
        server.daemon_threads = True
        server.team = self
        return server

    def started(self, host: str, port: int) -> ThreadingHTTPServer:
        server = self.http(host, port)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        return server

    def close(self, server: ThreadingHTTPServer) -> None:
        server.shutdown()
        server.server_close()
        self.store.close()
