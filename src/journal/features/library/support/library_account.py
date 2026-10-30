import json
import os
from pathlib import Path

from journal.config import Config
from journal.features.library.support.library_connection import LibraryConnection
from journal.support.rejection import Rejection
from journal.sync.hub_account import HubAccount

LIBRARIES_FOLDER = "libraries"


class LibraryAccount(HubAccount):
    """This journal's account on one team: the file connect writes in the libraries folder beside the database, named by the team's key, holding its name and address, this device's token and number, the person's account number, name and role, with the team's certificate authority beside it when its server signs its own; the home team's, the first joined, unless made for one team's key."""

    def __init__(self, config: Config) -> None:
        self.config, self.key = config, ""

    @classmethod
    def keyed(cls, config: Config, key: str) -> "LibraryAccount":
        account = cls(config)
        account.key = key
        return account

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
        return self.folder() / "root.crt"

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
        self.path().unlink()
        self.root_path().unlink(missing_ok=True)
        return address
