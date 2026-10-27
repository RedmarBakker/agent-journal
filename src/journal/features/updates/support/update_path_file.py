import json

from journal.config import Config
from journal.features.updates.support.update_pause import UPDATE_PAUSE_SECONDS
from journal.support.release import Release

STAYED = "stayed"


class UpdatePathFile:
    """The record install.sh keeps of a path of steps in .journal/runtime/update-path.json: where it starts and ends, its steps, the last step installed and the step that failed; a boot reads it and never clears it, and only the user's stay or a new update changes it."""

    def __init__(self, config: Config) -> None:
        self.path = config.home / "runtime" / "update-path.json"

    def record(self) -> dict:
        return json.loads(self.path.read_text()) if self.path.is_file() else {}

    def is_failed_at(self, version: str) -> bool:
        record = self.record()
        return record.get("reached") == version and bool(record.get("failed"))

    def is_walking_at(self, version: str, time: float) -> bool:
        record = self.record()
        if not record or record.get("failed") or record.get("to") == version:
            return False
        return version in (record.get("from"), *record.get("steps", [])) and time - self.path.stat().st_mtime <= UPDATE_PAUSE_SECONDS

    def problem(self, version: str) -> str:
        record = self.record()
        if not self.is_failed_at(version) or record.get(STAYED):
            return ""
        return f"The update to {record['to']} stopped at {version}: the step to {record['failed']} failed, and {version} keeps running. journal update retry tries {record['failed']} again; journal update stay keeps {version}"

    def stops(self) -> list[str]:
        record = self.record()
        return [*record["steps"], record["to"]]

    def step_version(self, version: str) -> str:
        return next(stop for stop in self.stops() if Release(stop).is_newer(Release(version)))

    def step_line(self, version: str) -> str:
        record, stops, in_hand = self.record(), self.stops(), self.step_version(version)
        return f"Updating from {record['from']} to {record['to']} in {len(stops)} steps: installing {in_hand}, step {stops.index(in_hand) + 1} of {len(stops)}"

    def stayed(self) -> None:
        self.path.write_text(json.dumps({**self.record(), STAYED: True}))

    def cleared(self) -> None:
        self.path.unlink(missing_ok=True)
