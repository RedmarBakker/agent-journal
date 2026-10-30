import hashlib
import json
import re
from dataclasses import dataclass
from typing import Mapping


SENSITIVE_KEY = re.compile(r"(?:^|_)(?:api_?key|access_?token|auth(?:orization)?|client_?secret|credential|password|private_?key|refresh_?token|secret|token)(?:$|_)")


@dataclass(frozen=True)
class Manifest:
    """An immutable, secret-free batch document addressed by its content digest."""

    batch_id: str
    document: str

    @classmethod
    def build(cls, batch_id: str, document: Mapping[str, object]) -> "Manifest":
        if not batch_id or any(not part.isalnum() and part not in "-_" for part in batch_id):
            raise ValueError("batch id must contain only letters, numbers, hyphens and underscores")
        cls.reject_secrets(document)
        encoded = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        return cls(batch_id, encoded)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.document.encode("utf-8")).hexdigest()

    def data(self) -> dict[str, object]:
        return json.loads(self.document)

    @classmethod
    def reject_secrets(cls, value: object) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                normalized = re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")
                if SENSITIVE_KEY.search(normalized):
                    raise ValueError(f"manifest cannot contain credential field {key}")
                cls.reject_secrets(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                cls.reject_secrets(item)
