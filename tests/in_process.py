import json

from journal.http.router import Router
from journal.http.support.identity import Identity
from journal.http.support.json_out import JsonOut
from journal.http.support.login_gate import LoginGate
from journal.http.support.request_reading import RequestReading


def posted(app, path: str, body: dict, headers: dict) -> tuple[int, dict]:
    """A POST answered by the journal's own router in this process, read as the server reads it and refused as its gate refuses, with no socket: the status and the answer's JSON."""
    return answered(app, "POST", path, json.dumps(body).encode(), headers)


def get_answer(app, path: str, headers: dict) -> tuple[int, dict]:
    """A GET answered by the journal's own router in this process, as posted answers a POST."""
    return answered(app, "GET", path, b"", headers)


def answered(app, method: str, path: str, raw: bytes, headers: dict) -> tuple[int, dict]:
    head = RequestReading.head(method, path, {"Content-Type": "application/json", **headers})
    request = RequestReading.read(head, raw, app.container.get(Identity))
    answer = app.container.get(LoginGate).refusal(request) or app.container.get(Router).route(request)
    return answer.status, json.loads(JsonOut.encoded(answer.body))
