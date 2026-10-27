import hashlib
import json
import ssl
import os
from pathlib import Path

from journal.config import Config
from journal.features.library.support.library_connection import LibraryConnection
from journal.support.rejection import Rejection
from journal.sync.team_url import TeamUrl

LIBRARIES_FOLDER = "libraries"


class LibraryAccount:
    """This journal's account on its team's library, one library at a time: the file connect writes in the libraries folder beside the database, named by the library's key, holding its address, this device's token and number, the person's account number, name and role, with the library's certificate authority beside it when its server signs its own."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def folder(self) -> Path:
        return self.config.home / LIBRARIES_FOLDER

    def path(self) -> Path:
        files = sorted(self.folder().glob("*.json"))
        if not files:
            raise Rejection("this journal is connected to no library: connect with journal library connect <url>")
        return files[0]

    def is_connected(self) -> bool:
        return self.folder().is_dir() and any(self.folder().glob("*.json"))

    def connection(self) -> LibraryConnection:
        return LibraryConnection.read(json.loads(self.path().read_text()))

    def address(self) -> str:
        return self.connection().address

    def token(self) -> str:
        return self.connection().token

    def root_path(self) -> Path:
        return self.folder() / "root.crt"

    def fingerprint(self) -> str:
        root = self.root_path()
        return hashlib.sha256(ssl.PEM_cert_to_DER_cert(root.read_text())).hexdigest() if root.is_file() else ""

    def invitation_url(self, code: str) -> str:
        return TeamUrl(self.address()).invitation(code, self.fingerprint())

    def write(self, connection: LibraryConnection) -> Path:
        self.folder().mkdir(parents=True, exist_ok=True)
        target = self.folder() / f"{connection.key}.json"
        draft = target.with_suffix(".draft")
        draft.write_text(json.dumps(connection.fields()))
        os.chmod(draft, 0o600)
        draft.replace(target)
        return target

    def disconnect(self) -> str:
        address = self.address()
        self.path().unlink()
        self.root_path().unlink(missing_ok=True)
        return address
