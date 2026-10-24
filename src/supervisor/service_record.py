import json
import os
import signal
import subprocess
from pathlib import Path


class ServiceRecord:
    """The process groups a supervisor's services run in, written down as they change, so the next supervisor of the same launch ends what a supervisor killed outright had left running."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._written: dict[str, list[str]] = {}

    def write(self, processes: dict[int, list[str]]) -> None:
        listed = {str(pid): command for pid, command in processes.items()}
        if listed == self._written or self.path == Path(os.devnull):
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(listed))
        self._written = listed

    def ended(self) -> None:
        for pid, command in self.recorded().items():
            if self.runs(int(pid), command):
                self.end_group(int(pid))
        self._written = {"": []}
        self.write({})

    def recorded(self) -> dict[str, list[str]]:
        try:
            decoded = json.loads(self.path.read_text())
        except (OSError, ValueError):
            return {}
        return {str(pid): [str(part) for part in command] for pid, command in decoded.items()} if isinstance(decoded, dict) else {}

    # a pid is reused by the system, so a recorded one is ended only while it still runs the command it was written with
    @staticmethod
    def runs(pid: int, command: list[str]) -> bool:
        shown = subprocess.run(["ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True, timeout=5).stdout.strip()
        return bool(shown) and shown.endswith(" ".join(command[1:]) or Path(command[0]).name)

    @staticmethod
    def end_group(pid: int) -> None:
        try:
            os.killpg(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            return
