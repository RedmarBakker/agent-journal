import json

from journal.config import Config

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

    def is_walking_at(self, version: str) -> bool:
        record = self.record()
        return version in record.get("steps", []) and not record.get("failed")

    def problem(self, version: str) -> str:
        record = self.record()
        if not self.is_failed_at(version) or record.get(STAYED):
            return ""
        return f"The update to {record['to']} stopped at {version}: the step to {record['failed']} failed, and {version} keeps running. journal update retry tries {record['failed']} again; journal update stay keeps {version}"

    def step_line(self, version: str) -> str:
        record = self.record()
        return f"Installed {version}, step {record['steps'].index(version) + 1} of {len(record['steps']) + 1} to {record['to']}; the next step is installing"

    def stayed(self) -> None:
        self.path.write_text(json.dumps({**self.record(), STAYED: True}))

    def cleared(self) -> None:
        self.path.unlink(missing_ok=True)
