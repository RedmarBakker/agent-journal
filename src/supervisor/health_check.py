import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HealthCheck:
    """How the supervisor tells that a service is well, as its launch file or its start request says in plain data: a URL that answers 200 within its timeout, its port read from a file when it names one, or a file written within a number of seconds; checked every few seconds once a grace after the service's start has passed, the service started again after a number of failures in a row."""

    url: str | None = None
    port_file: str | None = None
    file: str = ""
    max_age_seconds: float = 60.0
    timeout_seconds: float = 5.0
    grace_seconds: float = 30.0
    interval_seconds: float = 10.0
    failures: int = 3

    def fault(self) -> str:
        return self.url_fault(self.url) if self.url is not None else self.file_fault()

    def is_booted(self) -> bool:
        address = self.address(self.url or "")
        try:
            with urllib.request.urlopen(address, timeout=self.timeout_seconds) as answer:
                return answer.status == 200 and json.loads(answer.read()).get("phase") == "booted"
        except (OSError, ValueError):
            return False

    def address(self, url: str) -> str:
        if self.port_file is None:
            return url
        path = Path(self.port_file)
        port = path.read_text().strip() if path.is_file() else ""
        return url.replace("{port}", port) if port.isdigit() else ""

    def url_fault(self, url: str) -> str:
        address = self.address(url)
        if not address:
            return f"{self.port_file} names no port"
        try:
            with urllib.request.urlopen(address, timeout=self.timeout_seconds) as answer:
                return "" if answer.status == 200 else f"{address} answered {answer.status}"
        except urllib.error.HTTPError as refusal:
            return f"{address} answered {refusal.code}"
        except OSError as down:
            return f"{address} did not answer: {down}"

    def file_fault(self) -> str:
        path = Path(self.file)
        if not path.is_file():
            return f"{self.file} was never written"
        age_seconds = time.time() - path.stat().st_mtime
        return f"{self.file} was last written {age_seconds:.0f} seconds ago" if age_seconds > self.max_age_seconds else ""
