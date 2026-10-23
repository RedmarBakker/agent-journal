import json

from journal.http.router import Router
from journal.http.support.identity import Identity
from journal.http.support.json_out import JsonOut
from journal.http.support.login_gate import LoginGate
from journal.http.support.request_reading import RequestReading


def posted(app, path: str, body: dict, headers: dict) -> tuple[int, dict]:
    """A POST answered by the journal's own router in this process, read as the server reads it and refused as its gate refuses, with no socket: the status and the answer's JSON."""
    head = RequestReading.head("POST", path, {"Content-Type": "application/json", **headers})
    request = RequestReading.read(head, json.dumps(body).encode(), app.container.get(Identity))
    answer = app.container.get(LoginGate).refusal(request) or app.container.get(Router).route(request)
    return answer.status, json.loads(JsonOut.encoded(answer.body))
