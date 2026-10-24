import time
from dataclasses import dataclass, field, replace

from journal.support.actor import Actor
from journal.http.support.cli_post import CliPost
from journal.support.rejection import Rejection
from journal.support.missing_row import MissingRow

ENVIRONMENT_HEADER = "X-Journal-Env"
REQUEST_TIME_HEADER = "x-journal-request-at"
BOOT_WAIT_HEADER = "x-journal-boot-wait-ms"


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query: dict
    body: dict
    params: dict
    headers: dict
    actor: Actor
    files: dict = field(default_factory=dict)
    request_at: float = field(default_factory=time.time)
    boot_wait_seconds: float = 0.0

    @staticmethod
    def request_time(headers: dict) -> float:
        stamp = headers.get(REQUEST_TIME_HEADER, "")
        return int(stamp) / 1000 if stamp.isdigit() else time.time()

    def measured_path(self) -> str:
        if self.path == "/cli":
            return "/cli/" + " ".join(str(word) for word in self.body.get("argv", [])[:2])
        if self.path == "/cli/run":
            return "/cli/" + " ".join(CliPost.parsed(self.body["raw"]).argv[:2])
        return self.path

    @staticmethod
    def boot_wait(headers: dict) -> float:
        waited = headers.get(BOOT_WAIT_HEADER, "")
        return int(waited) / 1000 if waited.isdigit() else 0.0

    def boot_delayed(self, seconds: float) -> "Request":
        return replace(self, boot_wait_seconds=self.boot_wait_seconds + seconds, request_at=self.request_at + seconds)

    def is_boot_delayed(self) -> bool:
        return self.boot_wait_seconds > 0

    def with_params(self, params: dict) -> "Request":
        return replace(self, params=params)

    def number(self, name: str) -> int:
        value = self.params.get(name, "")
        if not value.isdigit():
            raise MissingRow("rows", value or "nothing")
        return int(value)

    def queried(self, name: str, default: float = 0.0) -> float:
        value = self.query.get(name)
        return float(value) if value else default

    @property
    def cookie(self) -> str:
        return self.headers.get("cookie", "")

    @property
    def host(self) -> str:
        return self.headers.get("host", "")

    @property
    def protocol(self) -> str:
        return self.headers.get("x-forwarded-proto", "")

    @property
    def environment(self) -> str:
        matched = self.headers.get(ENVIRONMENT_HEADER.lower()) or self.query.get("env")
        if not matched:
            raise Rejection(f"no environment: send it in the {ENVIRONMENT_HEADER} header")
        return matched
