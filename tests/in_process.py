import json

from journal.http.router import Router
from journal.http.support.file_response import FileResponse
from journal.http.support.identity import Identity
from journal.http.support.json_out import JsonOut
from journal.http.support.request_reading import RequestReading
from journal.support.listener_queue import ListenerQueue
from journal.http.support.supervisor_authentication import SupervisorRequestAuth


def posted(app, path: str, body: dict, headers: dict) -> tuple[int, dict]:
    """A POST answered by the journal's own router in this process, read as the server reads it and refused as its gate refuses, with no socket: the status and the answer's JSON."""
    return answered(app, "POST", path, json.dumps(body).encode(), headers)


def get_answer(app, path: str, headers: dict) -> tuple[int, dict]:
    """A GET answered by the journal's own router in this process, as posted answers a POST."""
    return answered(app, "GET", path, b"", headers)


got = get_answer


def answered(app, method: str, path: str, raw: bytes, headers: dict) -> tuple[int, dict]:
    answer = routed(app, method, path, raw, headers)
    return answer.status, json.loads(JsonOut.encoded(answer.body))


def file_answer(app, path: str, headers: dict) -> tuple[int, dict]:
    answer = routed(app, "GET", path, b"", headers)
    if isinstance(answer, FileResponse):
        return answer.status, {"content_type": answer.content_type, "headers": answer.headers(), "body": answer.body.decode("utf-8")}
    return answer.status, json.loads(JsonOut.encoded(answer.body))


def routed(app, method: str, path: str, raw: bytes, headers: dict):
    deferred = app.container.get(ListenerQueue)
    deferred.drain()
    answer = routed_without_listener_drain(app, method, path, raw, headers)
    deferred.drain()
    return answer


def posted_without_listener_drain(app, path: str, body: dict, headers: dict) -> tuple[int, dict]:
    answer = routed_without_listener_drain(app, "POST", path, json.dumps(body).encode(), headers)
    return answer.status, json.loads(JsonOut.encoded(answer.body))


def routed_without_listener_drain(app, method: str, path: str, raw: bytes, headers: dict):
    head = RequestReading.head(method, path, {"Content-Type": "application/json", **headers})
    request = RequestReading.read(
        head, raw, app.container.get(Identity), app.container.get(SupervisorRequestAuth)
    )
    return app.container.get(Router).route(request)
