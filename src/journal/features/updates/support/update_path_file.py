import json

from journal.config import Config
from journal.features.updates.support.update_path_record import UpdatePathRecord
from journal.features.updates.support.update_pause import UPDATE_PAUSE_SECONDS


class UpdatePathFile:
    """Where install.sh keeps the record of a path of steps, .journal/runtime/update-path.json: a boot reads it and never clears it, and only the user's close or a new update changes it; a path still under way counts only while the record was written within a step's time."""

    def __init__(self, config: Config) -> None:
        self.path = config.home / "runtime" / "update-path.json"

    def record(self) -> UpdatePathRecord:
        if not self.path.is_file():
            return UpdatePathRecord.empty()
        return UpdatePathRecord.read(json.loads(self.path.read_text()))

    def is_unfinished(self, version: str, time: float) -> bool:
        return self.record().is_unfinished(version) and time - self.path.stat().st_mtime <= UPDATE_PAUSE_SECONDS

    def closed(self) -> None:
        self.path.write_text(json.dumps(self.record().closed_record().as_data()))

    def cleared(self) -> None:
        self.path.unlink(missing_ok=True)
