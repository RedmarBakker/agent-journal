from dataclasses import dataclass
from typing import ClassVar

from journal.models.scoped import Scoped
from journal.models.verifier_state import VerifierState


@dataclass(frozen=True)
class Verifier(Scoped):
    """An agent the journal sends itself to judge one dismissal on the evidence in its brief, never a worker and never known to the main agent: its program and model, its session, the hash of the token its run proves itself with, its process, and whether it is still judging, gave its verdict or ended without one."""

    shared: ClassVar[bool] = False
    text_fields: ClassVar[tuple[str, ...]] = ("name", "brief")

    name: str = ""
    brief: str = ""
    provider: str = "claude"
    model: str = ""
    session: str = ""
    token_hash: str = ""
    pid: int = 0
    state: VerifierState = VerifierState.VERIFYING

    def running_as(self, pid: int) -> "Verifier":
        return self.with_(pid=pid)

    def judged(self) -> "Verifier":
        return self.with_(state=VerifierState.JUDGED, token_hash="")

    def ended(self) -> "Verifier":
        return self if self.state != VerifierState.VERIFYING else self.with_(state=VerifierState.ENDED, token_hash="")

    def is_verifying(self) -> bool:
        return self.state == VerifierState.VERIFYING
