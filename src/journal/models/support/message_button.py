from dataclasses import asdict, dataclass, field
from urllib.parse import urlparse

from journal.support.rejection import Rejection

WEB_SCHEMES = ("http", "https")
LINK_METHOD = "GET"
FORM_METHOD = "POST"


@dataclass(frozen=True)
class MessageButton:
    """A button under a message the agent sent: its label, the address it opens or posts to, a line on what pressing it does, and for a form post its hidden fields."""

    label: str
    action: str
    note: str
    method: str = LINK_METHOD
    fields: dict = field(default_factory=dict)

    @classmethod
    def link(cls, line: str) -> "MessageButton":
        label, action, note = cls.parts(line, 3)
        return cls(label, action, note).checked()

    @classmethod
    def form(cls, line: str) -> "MessageButton":
        label, action, note, *pairs = cls.parts(line, 4)
        return cls(label, action, note, FORM_METHOD, dict(cls.field_pair(pair) for pair in pairs)).checked()

    @staticmethod
    def parts(line: str, least: int) -> list[str]:
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < least or not all(parts[:3]):
            raise Rejection(f"a button is 'label|address|what pressing it does'{'|field=value' if least > 3 else ''}, not {line!r}")
        return parts

    @staticmethod
    def field_pair(pair: str) -> tuple[str, str]:
        name, sign, value = pair.partition("=")
        if not sign or not name.strip():
            raise Rejection(f"a form field is 'name=value', not {pair!r}")
        return name.strip(), value

    def checked(self) -> "MessageButton":
        address = urlparse(self.action)
        if address.scheme not in WEB_SCHEMES or not address.netloc:
            raise Rejection(f"a button opens a web address starting with http:// or https://, not {self.action!r}")
        return self

    def stored(self) -> dict:
        return asdict(self)
