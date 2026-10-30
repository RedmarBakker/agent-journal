import json
import os
from pathlib import Path

from journal.features.library.support.library_connection import LibraryConnection
from journal.support.rejection import Rejection
from journal.sync.hub_account import HubAccount

LIBRARIES_FOLDER = "libraries"
# one certificate authority for the whole folder, the home team's until a second team is connected
SHARED_ROOT_FILE = "root.crt"


class LibraryAccount(HubAccount):
    """This journal's account on one team: the file connect writes in the libraries folder beside the database, named by the team's key, holding its name and address, this device's token and number, the person's account number, name and role, with the team's certificate authority beside it when its server signs its own; the home team's, the first joined, unless made for one team's key."""

    def folder(self) -> Path:
        return self.config.home / LIBRARIES_FOLDER

    def path(self) -> Path:
        if self.key:
            return self.folder() / f"{self.key}.json"
        files = self.files()
        if not files:
            raise Rejection("this journal is connected to no team: connect with journal team connect <url>")
        homes = [path for path in files if json.loads(path.read_text()).get("home")]
        return (homes or files)[0]

    def files(self) -> list[Path]:
        return sorted(self.folder().glob("*.json"))

    def is_connected(self) -> bool:
        return self.path().is_file() if self.key else bool(self.files())

    def connection(self) -> LibraryConnection:
        return LibraryConnection.read(json.loads(self.path().read_text()))

    def address(self) -> str:
        return self.connection().address

    def token(self) -> str:
        return self.connection().token

    def root_path(self) -> Path:
        shared = self.folder() / SHARED_ROOT_FILE
        if not self.is_connected():
            return shared
        root = self.team_root_path()
        return root if root.is_file() else shared

    def team_root_path(self) -> Path:
        return self.folder() / f"{self.key or self.path().stem}.crt"

    def move_shared_root(self) -> None:
        shared = self.folder() / SHARED_ROOT_FILE
        if shared.is_file() and self.is_connected():
            shared.replace(self.team_root_path())

    def move_root(self, account: "LibraryAccount") -> None:
        if self.team_root_path().is_file():
            self.team_root_path().replace(account.team_root_path())

    def write(self, connection: LibraryConnection) -> Path:
        self.folder().mkdir(parents=True, exist_ok=True)
        target = self.folder() / f"{connection.key}.json"
        draft = target.with_suffix(".draft")
        draft.write_text(json.dumps({**connection.fields(), "home": self.is_home(target)}))
        os.chmod(draft, 0o600)
        draft.replace(target)
        return target

    def is_home(self, target: Path) -> bool:
        if target.is_file():
            return bool(json.loads(target.read_text()).get("home"))
        return not self.files()

    def disconnect(self) -> str:
        address = self.address()
        self.team_root_path().unlink(missing_ok=True)
        self.path().unlink()
        if not self.files():
            (self.folder() / SHARED_ROOT_FILE).unlink(missing_ok=True)
        return address
