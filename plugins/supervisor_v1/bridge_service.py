"""Journal plugin service that emits event references, never row contents."""

import hashlib
import json
import os
import signal
import socket
import threading
from pathlib import Path
from socketserver import StreamRequestHandler, ThreadingUnixStreamServer


EVENT_WAKE_KINDS = {
    "check_failed": ("checks", "failed_check", "check_id"),
    "task_test_failed": ("tasks", "stalled_task", "task_id"),
    "worker_silent": ("workers", "stale_worker", ("worker", "id")),
    "messages.created": ("messages", "message_to_supervisor", "id"),
    "question_posed": ("questions", "question_to_supervisor", "question_id"),
}
ALLOWED_EVENTS = {"tasks.created", "checks.created", "checks.updated", *EVENT_WAKE_KINDS}
HEALTH_ANSWER = '{"health":"up","service":"bridge"}'
HINTS_DIRECTORY = Path("/var/lib/journal-supervisor/hints")
MAX_HINTS = 1000
HINT_LOCK = threading.Lock()


def hint_from(line: str) -> dict[str, str] | None:
    """Return only the safe row reference from a subscribed journal event."""
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(event, dict) or event.get("event") not in ALLOWED_EVENTS:
        return None
    data = event.get("data")
    if not isinstance(data, dict):
        return None
    event_name = event["event"]
    table, wake_kind, identifier = EVENT_WAKE_KINDS.get(
        event_name, (event_name.split(".", 1)[0], "", "id"),
    )
    row_id = _event_row_id(data, identifier) if wake_kind else data.get("id")
    environment = event.get("environment")
    occurred_at = event.get("at")
    model_event = not wake_kind or event_name.endswith(".created")
    valid_row = (type(row_id) is int and row_id > 0) or isinstance(row_id, str) and bool(row_id)
    if not valid_row or model_event and data.get("table") != table:
        return None
    if not isinstance(environment, str) or not isinstance(occurred_at, str):
        return None
    hint = {"v": "1", "event": event_name, "at": occurred_at, "environment": environment,
            "table": table, "id": str(row_id)}
    if wake_kind:
        hint["event_kind"] = wake_kind
    return hint


def _event_row_id(data: dict[str, object], identifier: str | tuple[str, str]) -> object:
    if isinstance(identifier, tuple):
        nested = data.get(identifier[0])
        return nested.get(identifier[1]) if isinstance(nested, dict) else None
    return data.get(identifier)


def write_hint(directory: Path, hint: dict[str, str]) -> Path | None:
    """Atomically spool an idempotent, content-free event reference."""
    directory.mkdir(mode=0o750, parents=True, exist_ok=True)
    body = json.dumps(hint, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    name = hashlib.sha256(body).hexdigest() + ".json"
    target = directory / name
    temporary = directory / f".{name}.{os.getpid()}.tmp"
    with HINT_LOCK:
        if not target.exists() and sum(1 for _ in directory.glob("*.json")) >= MAX_HINTS:
            return None
        descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o640)
        try:
            with os.fdopen(descriptor, "wb") as output:
                output.write(body + b"\n")
            os.chmod(temporary, 0o640)
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
    return target


class EventHandler(StreamRequestHandler):
    def handle(self) -> None:
        line = self.rfile.readline().decode(errors="replace")
        if hint := hint_from(line):
            write_hint(HINTS_DIRECTORY, hint)
        self.wfile.write(b'{"v":1}\n')


class HealthHandler(StreamRequestHandler):
    def handle(self) -> None:
        self.rfile.readline()
        self.wfile.write((HEALTH_ANSWER + "\n").encode())


class LocalServer(ThreadingUnixStreamServer):
    daemon_threads = True
    allow_reuse_address = True


def open_server(path: Path, handler: type[StreamRequestHandler]) -> LocalServer:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.exists() and not path.is_socket():
        raise RuntimeError(f"refusing to replace a non-socket path: {path}")
    path.unlink(missing_ok=True)
    server = LocalServer(str(path), handler)
    path.chmod(0o600)
    return server


def main() -> None:
    event_path = Path(os.environ["JOURNAL_PLUGIN_SOCKET"])
    health_path = Path(os.environ["SUPERVISOR_HEALTH_SOCKET"])
    event_server = open_server(event_path, EventHandler)
    health_server = open_server(health_path, HealthHandler)
    servers = (event_server, health_server)
    threads = [threading.Thread(target=server.serve_forever, daemon=True) for server in servers]
    stopped = threading.Event()
    signal.signal(signal.SIGTERM, lambda signum, frame: stopped.set())
    signal.signal(signal.SIGINT, lambda signum, frame: stopped.set())
    try:
        for thread in threads:
            thread.start()
        while not stopped.wait(1):
            pass
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        for path in (event_path, health_path):
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
