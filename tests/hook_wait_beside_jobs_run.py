# Starts a journal and a thread of busy Python work beside it, so it runs for half a minute and is not in the default run: python3 -m pytest tests/hook_wait_beside_jobs_run.py.
import json
import threading
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from journal.config import Config
from journal.db.connection import Connection
from tests.main_journal import main_journal

BUSY_SECONDS = 30
HOOK_EVERY_SECONDS = 1
HOOK_BUDGET_SECONDS = 5.0
# a hook the journal refuses still answers, with this status
REFUSED_STATUS = 409


def hook_seconds(port: int, body: dict) -> float:
    began = time.monotonic()
    try:
        urlopen(Request(f"http://127.0.0.1:{port}/hooks/claude", data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main"}), timeout=60).read()
    except HTTPError as refused:
        assert refused.code == REFUSED_STATUS, f"the hook failed with {refused.code}"
    return time.monotonic() - began


def busy_work(until: float) -> None:
    while time.monotonic() < until:
        sum(number * number for number in range(10_000))


def write_lock_held(connection: Connection, until: float) -> None:
    with connection.transaction():
        while time.monotonic() < until:
            time.sleep(0.1)


def hooks_beside(work, app, port: int) -> list[float]:
    until = time.monotonic() + BUSY_SECONDS
    worker = threading.Thread(target=work, args=(until,), daemon=True)
    worker.start()
    times = []
    while time.monotonic() < until:
        times.append(hook_seconds(port, {"hook_event_name": "PreToolUse", "session_id": "s1", "tool_name": "Read", "tool_input": {"file_path": "a.py"}}))
        time.sleep(HOOK_EVERY_SECONDS)
    worker.join()
    return times


def test_a_hook_answers_within_its_budget_beside_half_a_minute_of_busy_python_work(tmp_path: Path):
    app = main_journal(Config(tmp_path, port=0))
    app.runtime().start()
    try:
        port = app.server().port
        hook_seconds(port, {"hook_event_name": "SessionStart", "session_id": "s1", "source": "startup"})
        times = hooks_beside(busy_work, app, port)
        assert max(times) < HOOK_BUDGET_SECONDS, f"a hook beside busy work took {max(times):.2f} s, past its {HOOK_BUDGET_SECONDS} s: {[round(t, 2) for t in times]}"
    finally:
        app.runtime().stop()


def test_a_hook_waits_on_a_write_lock_a_job_holds_for_half_a_minute(tmp_path: Path):
    app = main_journal(Config(tmp_path, port=0))
    app.runtime().start()
    try:
        port = app.server().port
        hook_seconds(port, {"hook_event_name": "SessionStart", "session_id": "s1", "source": "startup"})
        connection = app.container.get(Connection)
        times = hooks_beside(lambda until: write_lock_held(connection, until), app, port)
        print(f"\nhook seconds while a write lock is held: {[round(t, 2) for t in times]}")
    finally:
        app.runtime().stop()
