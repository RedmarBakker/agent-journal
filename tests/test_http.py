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
        assert [entry.kind for entry in app.container.get(Entries).scoped()] == ["ToolStarting"], "the hook script's post reaches the journal and is recorded"


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
