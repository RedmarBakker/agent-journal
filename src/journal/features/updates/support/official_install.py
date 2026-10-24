import os
import subprocess
from urllib.request import urlopen

from journal.config import Config
from journal.features.updates.support.release_source import REPOSITORY

# the official install command, as the README gives it
OFFICIAL_SCRIPT = "https://raw.githubusercontent.com/jessegall/agent-journal/main/install.sh"
# the longest the official install command may take: the release downloaded, installed and set up
OFFICIAL_INSTALL_SECONDS = 600
# the longest the official install script may take to download
DOWNLOAD_SECONDS = 30


class OfficialInstall:
    """The official install command from the README, main's install.sh fetched and piped to sh in the project root, aimed at one release, fetched by Python so it runs where curl is missing too; the journal runs it itself whenever its own installer fails, for whatever reason, leaning on nothing of the installed journal's code, so a broken updater can never strand a journal."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def ran(self, ref: str) -> subprocess.CompletedProcess:
        environ = {**os.environ, "AGENT_JOURNAL_REPO": REPOSITORY, "AGENT_JOURNAL_REF": ref, "AGENT_JOURNAL_YES": "1"}
        try:
            with urlopen(OFFICIAL_SCRIPT, timeout=DOWNLOAD_SECONDS) as answer:
                script = answer.read().decode()
        except OSError as unreachable:
            return subprocess.CompletedProcess(["sh"], 1, "", f"the official install script could not be fetched: {unreachable}")
        return subprocess.run(["sh"], input=script, cwd=self.config.root, env=environ, capture_output=True, text=True, timeout=OFFICIAL_INSTALL_SECONDS)
