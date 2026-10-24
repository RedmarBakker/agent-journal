import os
import subprocess

from journal.config import Config
from journal.features.updates.support.release_source import REPOSITORY

# the official install command, as the README gives it
OFFICIAL_SCRIPT = "https://raw.githubusercontent.com/jessegall/agent-journal/main/install.sh"
# the longest the official install command may take: the release downloaded, installed and set up
OFFICIAL_INSTALL_SECONDS = 600


class OfficialInstall:
    """The official install command from the README, curl of main's install.sh piped to sh in the project root, aimed at one release; the journal runs it itself whenever its own installer fails, for whatever reason, leaning on nothing of the installed journal's code, so a broken updater can never strand a journal."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def ran(self, ref: str) -> subprocess.CompletedProcess:
        environ = {**os.environ, "AGENT_JOURNAL_REPO": REPOSITORY, "AGENT_JOURNAL_REF": ref, "AGENT_JOURNAL_YES": "1"}
        return subprocess.run(["sh", "-c", f"curl -fsSL {OFFICIAL_SCRIPT} | sh"], cwd=self.config.root, env=environ, capture_output=True, text=True, timeout=OFFICIAL_INSTALL_SECONDS)
