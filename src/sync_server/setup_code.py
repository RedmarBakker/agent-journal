import hmac
import os
import secrets
from pathlib import Path

from sync_server.accounts import Accounts

SETUP_CODE_FILE = "setup-code"
# the letters of a setup code: no 0, O, 1, I or L, which read alike
LETTERS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


class SetupCode:
    """The one-time code that claims a team server with no admin yet: made when the server first serves, or given by TEAM_SETUP_CODE, kept in its data folder until the admin exists, and asked of the install that makes the admin."""

    def __init__(self, data: Path, accounts: Accounts) -> None:
        self.file, self.accounts = data / SETUP_CODE_FILE, accounts

    def issued(self) -> str:
        if not self.accounts.is_empty():
            self.discard()
            return ""
        if not self.file.is_file():
            self.file.parent.mkdir(parents=True, exist_ok=True)
            self.file.write_text(os.environ.get("TEAM_SETUP_CODE", "").strip().upper() or self.random_code())
        return self.file.read_text().strip()

    def matches(self, candidate: str) -> bool:
        if not self.file.is_file():
            return True
        return hmac.compare_digest(self.file.read_text().strip(), candidate.strip().upper())

    def discard(self) -> None:
        self.file.unlink(missing_ok=True)

    @staticmethod
    def random_code() -> str:
        letters = "".join(secrets.choice(LETTERS) for _ in range(8))
        return f"{letters[:4]}-{letters[4:]}"
