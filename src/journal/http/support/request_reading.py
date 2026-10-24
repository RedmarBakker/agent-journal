import json
from urllib.parse import parse_qs, urlsplit

from journal.http.support.identity import Identity
from journal.http.support.multipart import Multipart
from journal.http.support.request import Request
from journal.http.support.request_head import RequestHead


class RequestReading:
    """A Request read from one exchange's head and raw body, as the server reads every one."""

    @staticmethod
    def head(method: str, target: str, headers: dict[str, str]) -> RequestHead:
        return RequestHead(method, target, {name.lower(): value for name, value in headers.items()})

    @staticmethod
    def read(head: RequestHead, raw: bytes, identity: Identity) -> Request:
        url = urlsplit(head.target)
        query = {k: v[-1] for k, v in parse_qs(url.query).items()}
        person = identity.build(head.headers, head.cookie)
        request_at = Request.request_time(head.headers)
        waited = Request.boot_wait(head.headers)
        if head.content_type == "application/octet-stream":
            return Request(head.method, url.path, query, {"raw": raw}, {}, head.headers, person, request_at=request_at, boot_wait_seconds=waited)
        if head.content_type.startswith("multipart/form-data"):
            form = Multipart(head.content_type, raw)
            return Request(head.method, url.path, query, form.fields(), {}, head.headers, person, form.files(), request_at, waited)
        return Request(head.method, url.path, query, json.loads(raw) if raw else {}, {}, head.headers, person, request_at=request_at, boot_wait_seconds=waited)
