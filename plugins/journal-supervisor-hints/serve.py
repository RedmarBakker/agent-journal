#!/usr/bin/env python3
import json
import os
import socket
import sys
import threading
import time
from pathlib import Path


MAX_LOCAL_REQUESTS = 32
LOCAL_REQUESTS = threading.BoundedSemaphore(MAX_LOCAL_REQUESTS)
ALLOW_ANSWER = json.dumps({"v": 1, "answer": "allow"}, separators=(",", ":"))
HEALTH_ANSWER = json.dumps({"health": "ok"}, separators=(",", ":"))


def bridge_worker(data: Path, settings: dict) -> None:
    root = Path(os.environ["JOURNAL_ROOT"])
    sys.path.insert(0, str(root / "src"))
    from supervisor_bridge.bridge import NoAggregateBudgetProof, SupervisorBridge
    from supervisor_bridge.hints import HintSpool
    from supervisor_bridge.state import StateStore
    from supervisor_bridge.transport import JsonHttpConnection, SupervisorHttpClient, TransportError

    state = StateStore(settings.get("state_dir") or "/var/lib/journal-supervisor/transport")
    spool = HintSpool(data / "transport")
    url = settings.get("admission_url", "")
    token = os.environ.get("JOURNAL_SUPERVISOR_HINTS_ADMISSION_TOKEN_KEY", "")
    if not url or not token:
        state.record_failure("service_unauthorized" if not token else "service_unavailable", False)
        return
    try:
        client = SupervisorHttpClient(JsonHttpConnection(url, token))
    except TransportError:
        state.record_failure("service_unavailable", False)
        return
    bridge = SupervisorBridge(client, state, NoAggregateBudgetProof())
    while True:
        references, overflow = spool.peek_batch()
        if references or overflow:
            bridge.reconcile("hint")
            spool.acknowledge(references, overflow)
        time.sleep(0.5)


def event_answer(line: bytes, data: Path) -> str:
    root = Path(os.environ["JOURNAL_ROOT"])
    sys.path.insert(0, str(root / "src"))
    from supervisor_bridge.hints import HintError, HintSpool

    try:
        result = HintSpool(data / "transport").enqueue_event_line(line.decode("utf-8"))
    except (HintError, UnicodeDecodeError, OSError):
        result = {"v": 1, "answer": "allow"}
    return json.dumps(result, separators=(",", ":"))


def listen(path: str, handler, overload: str) -> None:
    socket_path = Path(path)
    socket_path.parent.mkdir(parents=True, exist_ok=True)
    if socket_path.exists():
        socket_path.unlink()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(path)
        os.chmod(path, 0o660)
        server.listen()
        while True:
            connection, _ = server.accept()
            if LOCAL_REQUESTS.acquire(blocking=False):
                threading.Thread(target=handle, args=(connection, handler), daemon=True).start()
            else:
                with connection:
                    connection.settimeout(1)
                    connection.sendall((overload + "\n").encode())


def handle(connection, handler) -> None:
    with connection:
        try:
            connection.settimeout(2)
            line = connection.makefile("rb").readline(65537)
            if len(line) > 65536:
                response = ALLOW_ANSWER
            else:
                response = handler(line)
            connection.sendall((response + "\n").encode())
        except OSError:
            return
        finally:
            LOCAL_REQUESTS.release()


def health_answer(line: bytes) -> str:
    return HEALTH_ANSWER


if __name__ == "__main__":
    settings = json.loads(Path(os.environ["JOURNAL_SETTINGS"]).read_text())
    data = Path(os.environ["JOURNAL_PLUGIN_DATA"])
    threading.Thread(target=bridge_worker, args=(data, settings), daemon=True).start()
    threading.Thread(target=listen, args=(os.environ["JOURNAL_PLUGIN_HEALTH_SOCKET"], health_answer, HEALTH_ANSWER), daemon=True).start()
    listen(os.environ["JOURNAL_PLUGIN_SOCKET"], lambda line: event_answer(line, data), ALLOW_ANSWER)
