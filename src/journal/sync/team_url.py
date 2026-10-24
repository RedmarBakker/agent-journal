import ipaddress
from dataclasses import dataclass
from urllib.parse import parse_qs, urlencode, urlsplit

JOIN_PATH = "/join"


@dataclass(frozen=True)
class TeamUrl:
    """A team server's URL as a person pastes it: the bare address of a server to connect to first, which the first journal to reach claims, or an invitation URL that also carries the invitation code and the fingerprint of the server's own certificate authority."""

    address: str
    code: str = ""
    fingerprint: str = ""

    @classmethod
    def parse(cls, text: str) -> "TeamUrl":
        written = text.strip().rstrip(".,;")
        parts = urlsplit(written if "://" in written else f"https://{written}")
        query = parse_qs(parts.query)
        return cls(f"{parts.scheme}://{parts.netloc.rstrip('.')}", query.get("code", [""])[0], query.get("fingerprint", [""])[0])

    def invitation(self, code: str, fingerprint: str) -> str:
        return f"{self.address}{JOIN_PATH}?{urlencode({'code': code, 'fingerprint': fingerprint})}"

    def is_invitation(self) -> bool:
        return bool(self.code)

    def is_https_ip(self) -> bool:
        parts = urlsplit(self.address)
        try:
            ipaddress.ip_address(parts.hostname)
        except ValueError:
            return False
        return parts.scheme == "https"
