import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlencode, urlsplit

JOIN_PATH = "/join"
SETUP_PATH = "/setup"


@dataclass(frozen=True)
class TeamUrl:
    """A team server's URL as a person pastes it: the bare address of a server to connect to first, which the first journal to reach claims, an invitation URL that also carries the invitation code and the fingerprint of the server's own certificate authority, or a new server's setup URL carrying the setup code that claims it."""

    address: str
    code: str = ""
    fingerprint: str = ""
    setup_code: str = ""

    @classmethod
    def parse(cls, text: str) -> "TeamUrl":
        cleaned = text.strip().rstrip(".,;")
        parts = urlsplit(cleaned if "://" in cleaned else f"https://{cleaned}")
        query = parse_qs(parts.query)
        address, code, fingerprint = f"{parts.scheme}://{parts.netloc.rstrip('.')}", query.get("code", [""])[0], query.get("fingerprint", [""])[0]
        if parts.path.rstrip("/") == SETUP_PATH:
            return cls(address, fingerprint=fingerprint, setup_code=code)
        return cls(address, code, fingerprint)

    def invitation(self, code: str, fingerprint: str) -> str:
        return f"{self.address}{JOIN_PATH}?{urlencode({'code': code, 'fingerprint': fingerprint})}"

    def host(self) -> str:
        return urlsplit(self.address).hostname or self.address

    def file_name(self) -> str:
        return re.sub(r"[^a-z0-9]+", "-", urlsplit(self.address).netloc.lower()).strip("-")

    def is_invitation(self) -> bool:
        return bool(self.code)

    def has_self_signed_certificate(self) -> bool:
        parts = urlsplit(self.address)
        if parts.scheme != "https":
            return False
        if parts.port not in (None, 443):
            return True
        try:
            ipaddress.ip_address(parts.hostname)
        except ValueError:
            return False
        return True
