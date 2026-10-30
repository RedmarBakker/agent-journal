import hmac
import os
import secrets
from pathlib import Path

from sync_server.refusal import Refusal

SETUP_CODE_FILE = "setup-code"
# a code the person installing the server chose, in place of the one it makes
SETUP_CODE_VARIABLE = "JOURNAL_TEAM_SETUP_CODE"


class SetupCode:
    """The code that claims a team server with no admin yet: the one set in JOURNAL_TEAM_SETUP_CODE, else one made at the first start and kept in the data folder, printed in the server's log; the first connection must send it, and it is removed once the admin exists."""

    def __init__(self, data: Path) -> None:
        self.path = data / SETUP_CODE_FILE

    def current(self) -> str:
        chosen = os.environ.get(SETUP_CODE_VARIABLE, "").strip()
        if chosen:
            return chosen
        if not self.path.is_file():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(secrets.token_urlsafe(18))
        return self.path.read_text().strip()

    def checked(self, sent: str) -> None:
        if not sent or not hmac.compare_digest(sent, self.current()):
            raise Refusal("a new team server is claimed only with its setup code: connect with the setup URL its log printed at its start, journal team connect <address>/setup?code=<code>")

    def used(self) -> None:
        self.path.unlink(missing_ok=True)
