"""Each way into the journal arrives and answers over HTTP on its real server: the one place the tests use a socket, as every other test calls the journal's router in-process (tests/in_process.py)."""

import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request as HttpRequest, urlopen

import pytest

from journal.app import App
from journal.config import Config
from journal.repositories.entries import Entries
from journal.repositories.scope import Scope
from journal.support.listener_queue import ListenerQueue

MAIN = 1


@pytest.fixture(scope="module")
def boot():
    def booted(root: Path, patch: pytest.MonkeyPatch) -> App:
        app = App(Config(root, port=0))
        app.container.get(ListenerQueue).start()
        app.server().start()
        return app
    return booted


def sent(app: App, method: str, path: str, body: dict | None = None, headers: dict | None = None) -> tuple[int, dict]:
    data = None if body is None else json.dumps(body).encode()
    request = HttpRequest(f"http://127.0.0.1:{app.server().port}{path}", data=data, method=method, headers={"Content-Type": "application/json", "X-Journal-Env": "main", **(headers or {})})
    try:
        with urlopen(request, timeout=5) as reply:
            return reply.status, json.loads(reply.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


def test_a_hook_posted_over_http_lands_as_an_entry_and_answers(app: App):
    status, body = sent(app, "POST", "/hooks/claude", {"hook_event_name": "PreToolUse", "session_id": "s1", "tool_name": "Read", "tool_input": {"file_path": "a.py"}})
    assert (status, body) == (200, {}), body
    with app.container.get(Scope).environment(MAIN):
        assert [entry.entry_type for entry in app.container.get(Entries).scoped()] == ["ToolStarting"], "the hook script's post reaches the journal and is recorded"


def test_a_command_posted_over_http_runs_and_answers_with_its_output(app: App):
    status, body = sent(app, "POST", "/cli", {"argv": ["task", "create", "the parser"], "env": "main", "session": None})
    assert status == 200 and body["code"] == 0 and "task 1" in body["text"], body


def test_a_viewer_request_over_http_answers_with_its_rows(app: App):
    sent(app, "POST", "/cli", {"argv": ["task", "create", "the parser"], "env": "main", "session": None})
    status, body = sent(app, "GET", "/journal/tasks")
    assert status == 200 and [row["title"] for row in body["rows"]] == ["the parser"], body


def test_a_refusal_and_a_missing_route_arrive_over_http_as_their_status(app: App):
    assert sent(app, "GET", "/journal/no-such-thing")[0] == 404, "a path no route takes is absent"
    status, body = sent(app, "POST", "/cli", {"argv": ["task", "start", "99"], "env": "main", "session": None})
    assert status == 200 and body["code"] != 0 and "no tasks row 99" in body["error"], body


def test_while_the_journal_boots_every_request_waits_and_is_answered_once_booted_its_wait_counted_apart(app: App):
    import threading
    import time
    from journal.engine.lifecycle import Lifecycle
    lifecycle = app.container.get(Lifecycle)
    lifecycle.booting()
    try:
        assert lifecycle.marker().read_text().isdigit(), "the booting file names the booting server's process, for the hook script"
        assert sent(app, "GET", "/journal/health") == (200, {"answering": True, "phase": "booting", "hooks_lost": [], "failing_requests": 0, "last_fault": ""}), "the health answer is the one thing answered while booting, and it names no environment whose hooks were lost"
        answers = {}
        stamp = str(int(time.time() * 1000))
        hook = threading.Thread(target=lambda: answers.update(hook=sent(app, "POST", "/hooks/claude", {"hook_event_name": "PreToolUse", "session_id": "s1", "tool_name": "Read", "tool_input": {"file_path": "a.py"}}, {"X-Journal-Request-At": stamp})))
        viewer = threading.Thread(target=lambda: answers.update(viewer=sent(app, "GET", "/journal/tasks")))
        hook.start(), viewer.start()
        time.sleep(0.4)
        assert not answers, "held while the journal boots"
    finally:
        lifecycle.booted()
    hook.join(5), viewer.join(5)
    assert answers["hook"][0] == 200 and answers["viewer"][0] == 200, answers
    assert not lifecycle.marker().exists() and sent(app, "GET", "/journal/health")[1]["phase"] == "booted"
    with app.container.get(Scope).environment(MAIN):
        [entry] = [entry for entry in app.container.get(Entries).scoped() if entry.entry_type == "ToolStarting" and "hook_ms" in entry.data]
    assert entry.data["boot_wait_ms"] >= 350, "the hook's entry says how long it waited for the boot"
    assert entry.data["hook_ms"] < entry.data["boot_wait_ms"], "and its own time leaves the wait out"


def test_every_hook_event_carries_the_seconds_it_waited_for_the_boot():
    from journal.events.agent.stop import Stop
    event = Stop().boot_delayed(1.5)
    assert event.is_boot_delayed() and event.boot_wait_seconds == 1.5
    assert not Stop().is_boot_delayed()


def test_the_runtime_loads_while_booting_and_starts_its_workers_and_jobs_only_once_booted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from journal.engine.lifecycle import Lifecycle
    from journal.engine.lifecycle_phase import LifecyclePhase
    app = App(Config(tmp_path, port=0))
    runtime = app.runtime()
    seen = {}
    booted = Lifecycle.booted
    def noted(lifecycle):
        seen.update(listening=bool(runtime.server._bound), jobs=runtime.jobs._thread is not None, phase=lifecycle.phase)
        booted(lifecycle)
    monkeypatch.setattr(Lifecycle, "booted", noted)
    runtime.start()
    try:
        assert seen == {"listening": True, "jobs": False, "phase": LifecyclePhase.BOOTING}, "the server listens while booting, and no job runs before it is booted"
        assert runtime.jobs._thread is not None and app.container.get(Lifecycle).is_booted()
    finally:
        runtime.stop()
