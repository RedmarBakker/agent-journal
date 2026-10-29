"""Journal plugin service that emits event references, never row contents."""

import hashlib
import json
import os
import signal
import socket
import threading
from pathlib import Path
from socketserver import StreamRequestHandler, ThreadingUnixStreamServer


ALLOWED_EVENTS = {"tasks.created", "checks.created", "checks.updated"}
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
    table = event_name.split(".", 1)[0]
    row_id = data.get("id")
    environment = event.get("environment")
    occurred_at = event.get("at")
    if data.get("table") != table or not isinstance(row_id, str) or not row_id:
        return None
    if not isinstance(environment, str) or not isinstance(occurred_at, str):
        return None
    return {"v": "1", "event": event_name, "at": occurred_at, "environment": environment, "table": table, "id": row_id}


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
