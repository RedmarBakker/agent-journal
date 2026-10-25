from sync_server.accounts import Accounts
from sync_server.change_log import ChangeLog
from sync_server.copied_row import CopiedRow
from sync_server.db.store import Store
from sync_server.file_store import FileStore
from sync_server.leases import Leases
from sync_server.logged_change import UPDATED, WITHDRAWN, LoggedChange
from sync_server.server_clock import ServerClock

OWNER = "owner"
DRIVER_FIELDS = ("driver", "driver_agent")


class Departure:
    """What a person leaving the team, or removed from it, leaves on the team server: every lease their devices hold let go, the hub plans and tasks they drive no longer named as theirs, and every environment they share withdrawn with its rows and the links touching them, kept by them, so the server and every colleague's journal let go of it and their own journal keeps it, as it keeps their copies and their own environments; the server reads the owner links, the environments' fields and the driven rows for it, as it reads a hub row's."""

    def __init__(self, store: Store, log: ChangeLog, leases: Leases, files: FileStore, accounts: Accounts, clock: ServerClock) -> None:
        self.store, self.log, self.leases, self.files, self.accounts, self.clock = store, log, leases, files, accounts, clock

    def left(self, account_id: int, device_id: int, actor: str) -> int:
        rows, name, now = self.log.copied_rows(), self.accounts.find(account_id).name, self.clock.time()
        withdrawn = self.shared_rows(rows, account_id)
        driven = [row for row in rows if row.row_table in ("tasks", "plans") and name and row.fields.get("driver") == name]
        with self.store.transaction():
            self.leases.release_person(account_id)
            for row in driven:
                self.log.appended(LoggedChange(row.row_table, row.row, UPDATED, actor, account_id, device_id, {field: "" for field in DRIVER_FIELDS}, {field: now for field in DRIVER_FIELDS}))
            for table, number in withdrawn:
                self.log.appended(LoggedChange(table, number, WITHDRAWN, actor, account_id, device_id, kept_by=f"user:{account_id}"))
        for table, number in withdrawn:
            self.files.removed(table, number)
        return len(withdrawn)

    @staticmethod
    def shared_rows(rows: list[CopiedRow], account_id: int) -> list[tuple[str, int]]:
        owned = {int(str(row.fields.get("target")).rpartition(":")[2]) for row in rows if row.row_table == "links" and row.fields.get("kind") == OWNER and row.fields.get("source") == f"users:{account_id}" and str(row.fields.get("target", "")).startswith("environments:")}
        shared = {row.row for row in rows if row.row_table == "environments" and row.row in owned and row.fields.get("kind", "local") == "local" and row.fields.get("team_key")}
        contents = [(row.row_table, row.row) for row in rows if row.row_table != "environments" and row.fields.get("environment_id") in shared]
        refs = {f"environments:{number}" for number in shared} | {f"{table}:{number}" for table, number in contents}
        links = [("links", row.row) for row in rows if row.row_table == "links" and (row.fields.get("source") in refs or row.fields.get("target") in refs)]
        return [*dict.fromkeys([*links, *contents, *(("environments", number) for number in shared)])]
