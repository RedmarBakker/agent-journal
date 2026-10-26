import hashlib
import json
import os
import ssl
import re
import socket
import threading
from pathlib import Path

from journal.config import Config
from journal.models.environment import UNKNOWN_TEAM_KEY
from journal.support.actor import Actor
from journal.support.caller import LOCAL_USER
from journal.support.release import Release
from journal.sync.team_url import TeamUrl
from sync_server.account import ADMIN

TEAM_FILE = "team.json"
TEAMS_FOLDER = "teams"
ROOT_FILE = "team-root.crt"
PREFIX_FILE = "team-prefix"


class TeamAccount:
    """This journal's place in a team: whether it has joined one and which device of the team this machine is, whether it holds the team's upgrade, and the team's key and number T, read from the file the join writes in the teams folder beside the database, named by the team's key; the home team's, the first joined, unless made for one team's key; an account from before teams had keys is read from team.json until its key is recorded, which moves it into the teams folder."""

    def __init__(self, config: Config) -> None:
        self.config, self.key = config, ""

    @classmethod
    def keyed(cls, config: Config, key: str) -> "TeamAccount":
        account = cls(config)
        account.key = key
        return account

    def is_joined(self) -> bool:
        return self.path().is_file()

    def path(self) -> Path:
        if self.key:
            return self.config.home / TEAMS_FOLDER / f"{self.key}.json"
        files = sorted((self.config.home / TEAMS_FOLDER).glob("*.json"))
        homes = [path for path in files if json.loads(path.read_text()).get("home", True)] if len(files) > 1 else files
        return next(iter(homes or files), self.config.home / TEAM_FILE)

    def team_key(self) -> str:
        return str(self.contents().get("team_key", UNKNOWN_TEAM_KEY)) if self.is_joined() else ""

    def is_on_hub(self) -> bool:
        return bool(self.contents().get("on_hub", False))

    def record_on_hub(self) -> None:
        self.write({**self.contents(), "on_hub": True})

    def team_number(self) -> int:
        return int(self.contents().get("team_number", 0))

    def record_team(self, key: str, number: int) -> None:
        self.write({**self.contents(), "team_key": key, "team_number": number})

    def device(self) -> str:
        return str(self.contents().get("device", ""))

    def is_seed_writer(self) -> bool:
        return not self.is_joined() or self.is_upgrader()

    def is_upgrader(self) -> bool:
        return bool(self.contents().get("upgrade", False))

    def address(self) -> str:
        return self.contents().get("address", "")

    def token(self) -> str:
        return self.contents().get("token", "")

    def sequence(self) -> int:
        return int(self.contents().get("sequence", 0))

    def record_sequence(self, sequence: int) -> None:
        self.write({**self.contents(), "sequence": sequence})

    def record_pull(self, sequence: int, team_version: str) -> None:
        self.write({**self.contents(), "sequence": sequence, "team_version": team_version})

    def team_version(self) -> str:
        return str(self.contents().get("team_version", ""))

    def allows(self, release: Release) -> bool:
        return not self.is_joined() or release.version == self.team_version()

    def leave(self, time: float) -> Path:
        backup = self.config.home / f"{TEAM_FILE}.left-{int(time)}"
        self.path().replace(backup)
        (self.config.home / ROOT_FILE).unlink(missing_ok=True)
        return backup

    def write(self, contents: dict) -> None:
        held = self.path()
        path = self.config.home / TEAMS_FOLDER / f"{contents['team_key']}.json" if contents.get("team_key") else held
        path.parent.mkdir(exist_ok=True)
        draft = path.with_name(f"{path.stem}.{os.getpid()}-{threading.get_ident()}.draft")
        draft.write_text(json.dumps(contents))
        os.chmod(draft, 0o600)
        draft.replace(path)
        if held != path:
            held.unlink(missing_ok=True)

    def contents(self) -> dict:
        return json.loads(self.path().read_text()) if self.is_joined() else {}

    def user_number(self) -> int:
        return int(self.contents().get("account_id", LOCAL_USER))

    def root_path(self) -> Path:
        return self.config.home / ROOT_FILE

    def fingerprint(self) -> str:
        root = self.root_path()
        return hashlib.sha256(ssl.PEM_cert_to_DER_cert(root.read_text())).hexdigest() if root.is_file() else ""

    def invitation_url(self, code: str) -> str:
        return TeamUrl(self.address()).invitation(code, self.fingerprint())

    def device_name(self) -> str:
        return socket.gethostname()

    def phone_actor(self, phone_id: int) -> Actor:
        return Actor.user(self.user_number()) if self.is_joined() else Actor.phone(phone_id)

    def write_prefix(self, name: str) -> str:
        prefix = re.sub(r"[^a-z0-9]+", "-", name.split()[0].lower() if name.split() else "").strip("-") or f"user{self.user_number()}"
        (self.config.home / PREFIX_FILE).write_text(prefix)
        return prefix

    def prefix(self) -> str:
        prefix_file = self.config.home / PREFIX_FILE
        return prefix_file.read_text().strip() if prefix_file.is_file() else ""

    def personal_name(self, name: str) -> str:
        prefix = self.prefix()
        return f"{prefix}-{name}" if prefix and not name.startswith(f"{prefix}-") else name

    def is_admin(self) -> bool:
        return self.contents().get("role") == ADMIN

    def is_chat_holder(self) -> bool:
        return bool(self.contents().get("holds_chat", False))

    def held_sessions(self) -> list[str]:
        return list(self.contents().get("sessions", []))

    def record_held_sessions(self, names: list[str]) -> None:
        self.write({**self.contents(), "sessions": sorted(set(names))})
