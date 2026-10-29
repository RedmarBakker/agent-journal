import fcntl
import hashlib
import json
import os
import tempfile
from pathlib import Path


MAX_HINTS = 256
MAX_BATCH = 100
MAX_HINT_FILE_BYTES = 131072
ROW_EVENTS = frozenset(
    f"{table}.{event}"
    for table in ("plans", "phases", "tasks", "checks")
    for event in ("created", "updated", "deleted")
)


class HintError(ValueError):
    """A plugin row hint is not one of the bounded journal row references."""


class HintSpool:
    """An atomic transport-only queue of row references; no event prose is kept."""

    def __init__(self, directory: Path | str):
        self.directory = Path(directory)
        self.path = self.directory / "hints.json"
        self.lock_path = self.directory / ".hints.lock"

    def enqueue_event_line(self, line: str) -> dict:
        try:
            event = json.loads(line)
        except (TypeError, json.JSONDecodeError) as error:
            raise HintError("plugin event line is not JSON") from error
        if (
            not isinstance(event, dict)
            or type(event.get("v")) is not int
            or event.get("v") != 1
            or not isinstance(event.get("event"), str)
            or event.get("event") not in ROW_EVENTS
        ):
            raise HintError("plugin event is outside the row hint allowlist")
        data = event.get("data")
        if not isinstance(data, dict) or set(data) not in ({"table", "id", "by"}, {"table", "id", "by", "changed"}):
            raise HintError("plugin event has an unsupported row reference")
        table = data["table"]
        row_id = data["id"]
        if not isinstance(table, str) or table not in {"plans", "phases", "tasks", "checks"} or event["event"].split(".", 1)[0] != table:
            raise HintError("plugin event table is not enabled")
        if type(row_id) is not int or row_id < 1:
            raise HintError("plugin row id must be a positive integer")
        reference = {"table": table, "id": row_id}
        key = hashlib.sha256(f"{table}:{row_id}".encode()).hexdigest()
        with self.locked():
            state = self.read_locked()
            references = state["references"]
            if not any(item["key"] == key for item in references):
                if len(references) < MAX_HINTS:
                    references.append({"key": key, "ref": reference})
                else:
                    state["overflow"] = True
            self.write_locked(state)
        return {"v": 1, "answer": "allow"}

    def peek_batch(self) -> tuple[list[dict], bool]:
        with self.locked():
            state = self.read_locked()
            return ([dict(item["ref"]) for item in state["references"][:MAX_BATCH]], bool(state["overflow"]))

    def acknowledge(self, references: list[dict], overflow: bool) -> None:
        keys = {
            hashlib.sha256(f"{reference['table']}:{reference['id']}".encode()).hexdigest()
            for reference in references
        }
        with self.locked():
            state = self.read_locked()
            state["references"] = [item for item in state["references"] if item["key"] not in keys]
            if overflow:
                state["overflow"] = False
            self.write_locked(state)

    def read_locked(self) -> dict:
        if not self.path.exists():
            return {"references": [], "overflow": False}
        try:
            raw = self.path.read_bytes()
            if len(raw) > MAX_HINT_FILE_BYTES:
                raise HintError("plugin hint spool exceeds the byte limit")
            state = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise HintError("plugin hint spool is unreadable") from error
        if not isinstance(state, dict) or set(state) != {"references", "overflow"}:
            raise HintError("plugin hint spool has an unsupported shape")
        if not isinstance(state["references"], list) or len(state["references"]) > MAX_HINTS or type(state["overflow"]) is not bool:
            raise HintError("plugin hint spool exceeds its fixed bounds")
        for item in state["references"]:
            if not isinstance(item, dict) or set(item) != {"key", "ref"}:
                raise HintError("plugin hint spool contains an invalid item")
            reference = item["ref"]
            if not isinstance(reference, dict) or set(reference) != {"table", "id"}:
                raise HintError("plugin hint spool contains an invalid reference")
            if not isinstance(reference["table"], str) or reference["table"] not in {"plans", "phases", "tasks", "checks"} or type(reference["id"]) is not int or reference["id"] < 1:
                raise HintError("plugin hint spool contains an out-of-scope reference")
            expected_key = hashlib.sha256(f"{reference['table']}:{reference['id']}".encode()).hexdigest()
            if item["key"] != expected_key:
                raise HintError("plugin hint spool contains an invalid reference key")
        return state

    def write_locked(self, state: dict) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(prefix=".hints-", dir=self.directory)
        try:
            os.fchmod(handle, 0o660)
            with os.fdopen(handle, "w", encoding="utf-8") as output:
                json.dump(state, output, sort_keys=True, separators=(",", ":"))
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
            directory = os.open(self.directory, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def locked(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.lock_path, os.O_CREAT | os.O_RDWR, 0o660)
        return HintLock(descriptor)


class HintLock:
    """Cross-process lock for atomic durable hint updates."""

    def __init__(self, descriptor: int):
        self.descriptor = descriptor

    def __enter__(self):
        fcntl.flock(self.descriptor, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc, traceback):
        fcntl.flock(self.descriptor, fcntl.LOCK_UN)
        os.close(self.descriptor)

