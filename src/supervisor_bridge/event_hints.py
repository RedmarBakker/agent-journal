import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

from supervisor_bridge.contracts import EVENT_WAKE_KINDS


EVENT_ID = re.compile(r"[a-f0-9]{64}")
MAX_HINTS = 1000
MAX_STATE_BYTES = 65536
MAX_HINT_BYTES = 4096
HINT_FIELDS = frozenset({"v", "event", "at", "environment", "table", "id"})


class EventHintDirectory:
    """Reads the bounded row-reference files written by the journal event bridge."""

    def __init__(self, directory: Path | str, state_file: Path | str):
        self.directory = Path(directory)
        self.state_file = Path(state_file)

    def pending(self) -> list[dict[str, str]]:
        completed = self.completed()
        hints = []
        paths = self.directory.glob("*.json") if self.directory.is_dir() else ()
        for path in paths:
            event_id = path.stem
            if event_id in completed or not EVENT_ID.fullmatch(event_id):
                continue
            raw = path.read_bytes()
            body = raw.removesuffix(b"\n")
            if len(body) > MAX_HINT_BYTES or hashlib.sha256(body).hexdigest() != event_id:
                continue
            hint = json.loads(body)
            event_kind = hint.get("event_kind", "") if isinstance(hint, dict) else None
            if not isinstance(event_kind, str):
                continue
            if (not isinstance(hint, dict) or set(hint) not in (HINT_FIELDS, HINT_FIELDS | {"event_kind"})
                    or hint.get("v") != "1" or not isinstance(hint.get("event"), str)):
                continue
            if not isinstance(hint.get("at"), str) or not isinstance(hint.get("environment"), str):
                continue
            if not isinstance(hint.get("table"), str) or not isinstance(hint.get("id"), str):
                continue
            hints.append({"event_id": event_id, "event_kind": event_kind if event_kind in EVENT_WAKE_KINDS else "",
                          "at": hint["at"]})
        return sorted(hints, key=lambda hint: (hint["at"], hint["event_id"]))[:MAX_HINTS]

    def acknowledge(self, event_id: str) -> None:
        if not EVENT_ID.fullmatch(event_id):
            raise ValueError("event hint id is invalid")
        completed = self.completed()
        if event_id in completed:
            return
        completed.append(event_id)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".event-hints-", dir=self.state_file.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as output:
                json.dump({"completed": completed[-MAX_HINTS:]}, output, separators=(",", ":"))
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.state_file)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def completed(self) -> list[str]:
        if not self.state_file.exists():
            return []
        raw = self.state_file.read_bytes()
        if len(raw) > MAX_STATE_BYTES:
            raise ValueError("event hint state exceeds the fixed limit")
        state = json.loads(raw)
        if (not isinstance(state, dict) or set(state) != {"completed"}
                or not isinstance(state["completed"], list)
                or len(state["completed"]) > MAX_HINTS
                or any(not isinstance(value, str) or not EVENT_ID.fullmatch(value) for value in state["completed"])):
            raise ValueError("event hint state is invalid")
        return state["completed"]
