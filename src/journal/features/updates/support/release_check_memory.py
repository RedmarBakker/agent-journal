import json
import os
import threading
from pathlib import Path

from journal.features.updates.support.release_check import ReleaseCheck

# the variable that names the folder a machine keeps what every journal on it shares; tests point it at a scratch folder
MACHINE_VARIABLE = "AGENT_JOURNAL_MACHINE"
MEMORY_FILE = "release-check.json"


class ReleaseCheckMemory:
    """The release check every journal on this machine shares, kept in one file of the machine folder, so a journal that restarts counts its next look from the last one any journal made and never asks again at its start."""

    def path(self) -> Path:
        folder = Path(os.environ[MACHINE_VARIABLE]) if MACHINE_VARIABLE in os.environ else Path.home() / ".journal"
        return folder / MEMORY_FILE

    def last(self) -> ReleaseCheck:
        try:
            return ReleaseCheck.parsed(json.loads(self.path().read_text()))
        except (OSError, ValueError):
            return ReleaseCheck()

    def store(self, check: ReleaseCheck) -> None:
        path = self.path()
        path.parent.mkdir(parents=True, exist_ok=True)
        draft = path.with_name(f"{path.stem}.{os.getpid()}-{threading.get_ident()}.draft")
        draft.write_text(json.dumps(check.published()))
        draft.replace(path)
