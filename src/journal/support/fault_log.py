import sys
import threading
import time
import traceback
from pathlib import Path

from journal.config import Config
from journal.support.recorded_fault import RecordedFault
from journal.version import VERSION

FAULTS_FILE = "faults.jsonl"
FAULT_TEXT_CHARACTERS = 300


class FaultLog:
    """Every fault the journal meets that it carries on past, a request that raised, a job's tick or deferred work: its traceback written to the log as before, and one line in the runtime's faults file naming where it happened, its type, its first words and its frames, never the values it held, which the faults feature sends on when the user names a place to send them."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.lock = threading.Lock()

    def path(self) -> Path:
        return self.config.home / "runtime" / FAULTS_FILE

    def reported(self, place: str, fault: BaseException) -> None:
        sys.stderr.write(f"{place} failed:\n{''.join(traceback.format_exception(fault))}")
        frames = tuple({"filename": Path(frame.filename).name, "function": frame.name, "lineno": frame.lineno} for frame in traceback.extract_tb(fault.__traceback__))
        recorded = RecordedFault(time.time(), place, type(fault).__name__, str(fault)[:FAULT_TEXT_CHARACTERS], frames, VERSION)
        with self.lock:
            self.path().parent.mkdir(parents=True, exist_ok=True)
            with self.path().open("a") as faults:
                faults.write(recorded.line() + "\n")

    def drained(self) -> list[RecordedFault]:
        with self.lock:
            if not self.path().is_file():
                return []
            lines = self.path().read_text().splitlines()
            self.path().unlink()
        return [RecordedFault.read(line) for line in lines if line.strip()]

    def unsent(self, fault: RecordedFault, reason: BaseException) -> None:
        sys.stderr.write(f"a fault at {fault.place} could not be sent on: {reason}\n")
