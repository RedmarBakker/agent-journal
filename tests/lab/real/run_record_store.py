import json
import os
import stat
import tempfile
from pathlib import Path

from tests.lab.real.run_record import RunRecord


class RunRecordStore:
    """Persist immutable real-run records in a private evidence directory."""

    def write(self, evidence: Path, record: RunRecord) -> Path:
        self.validate_evidence(evidence)
        path = evidence / "run-record.json"
        if path.is_symlink():
            raise ValueError("run record cannot replace a symlink")
        descriptor, temporary = tempfile.mkstemp(prefix=".run-record-", dir=evidence)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as target:
                json.dump(record.to_document(), target, sort_keys=True, separators=(",", ":"), allow_nan=False)
                target.write("\n")
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary, path)
            directory = os.open(evidence, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return path

    def read(self, path: Path) -> RunRecord:
        if not path.is_absolute() or any(part.is_symlink() for part in (path, *path.parents)):
            raise ValueError("run record cannot use a relative or symlink path")
        if not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise ValueError("run record must be a private regular file")
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError("run record must be a JSON object")
        return RunRecord.from_document(document)

    @staticmethod
    def validate_evidence(evidence: Path) -> None:
        if not evidence.is_absolute() or evidence.name != "evidence":
            raise ValueError("run evidence must use its absolute isolated evidence directory")
        if any(part.is_symlink() for part in (evidence, *evidence.parents)):
            raise ValueError("run evidence cannot use a symlink path")
        if not evidence.is_dir() or stat.S_IMODE(evidence.stat().st_mode) & 0o077:
            raise ValueError("run evidence directory must be private to its owner")
