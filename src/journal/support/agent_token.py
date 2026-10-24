import hashlib
import hmac
import secrets
from dataclasses import dataclass

TOKEN_BYTES = 32


@dataclass(frozen=True)
class AgentToken:
    """The secret a sent agent's run, a worker's or a verifier's, uses to prove who it is: created new for each run, with only its hash stored on its row."""

    text: str

    @classmethod
    def random(cls) -> "AgentToken":
        return cls(secrets.token_urlsafe(TOKEN_BYTES))

    @staticmethod
    def hashed(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def digest(self) -> str:
        return self.hashed(self.text)

    @classmethod
    def is_proof(cls, text: str | None, digest: str) -> bool:
        return text is not None and bool(digest) and hmac.compare_digest(cls.hashed(text), digest)
