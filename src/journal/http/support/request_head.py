from dataclasses import dataclass


@dataclass(frozen=True)
class RequestHead:
    """An exchange's method, target and headers by lowered name, before its body is read."""

    method: str
    target: str
    headers: dict[str, str]

    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "")

    @property
    def cookie(self) -> str:
        return self.headers.get("cookie", "")
