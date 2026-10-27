import os
import re
import subprocess
from pathlib import Path
from urllib.request import urlopen

from journal.config import Config
from journal.support.rejection import Rejection

GITHUB = re.compile(r"^(?:https://github\.com/|git@github\.com:)(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$")
DOWNLOAD_SECONDS = 30


# why an install runs when the updater that asks for it names no reason
UPDATE_REASON = "updating to the latest release"


class ReleaseInstaller:
    """The new release's own install.sh, the one the README gives, started from the project root as a process of its own, detached from this journal so it outlives it: the script, all new code, swaps the release into .journal/src, runs journal setup and restarts the running journals on it; this journal only starts it and records that it did, in runtime/update.log. The reason of a run has a plain default, since an updater from before 2026-10-24 calls it with the ref and the repository alone."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.log = config.home / "runtime" / "update.log"

    def run(self, ref: str, repository: str, reason: str = UPDATE_REASON) -> None:
        self.log.parent.mkdir(parents=True, exist_ok=True)
        script = self.log.with_name("install.sh")
        with self.log.open("w") as log:
            log.write(f"installing {ref} of {repository}: {reason}\n")
        try:
            with urlopen(self.script_path(repository, ref), timeout=DOWNLOAD_SECONDS) as answer:
                script.write_bytes(answer.read())
            subprocess.Popen(["sh", str(script)], cwd=self.config.root, env={**os.environ, "AGENT_JOURNAL_REPO": repository, "AGENT_JOURNAL_REF": ref, "AGENT_JOURNAL_YES": "1"},
                             stdout=self.log.open("a"), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        except OSError as error:
            with self.log.open("a") as log:
                log.write(f"the install could not start: {error}\n")
            raise Rejection(f"the install of {ref} could not start: {error}") from error

    @staticmethod
    def script_path(repository: str, ref: str) -> str:
        rows = GITHUB.match(repository)
        if rows is None:
            raise Rejection(f"the journal installs from GitHub only: {repository} is no GitHub address")
        return f"https://raw.githubusercontent.com/{rows['owner']}/{rows['repo']}/{ref}/install.sh"
