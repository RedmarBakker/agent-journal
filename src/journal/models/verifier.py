from dataclasses import dataclass
from typing import ClassVar

from journal.events.rows.verifier_exited import VerifierExited
from journal.models.helper import Helper
from journal.models.verifier_state import VerifierState


@dataclass(frozen=True)
class Verifier(Helper):
    """An agent the journal sends itself to judge one dismissal on the evidence in its brief, never a worker and never known to the main agent: its program and model, its session, the hash of the token its run proves itself with, its process, and whether it is still judging, gave its verdict and waits idle for the next judgement, or ended without one."""

    shared: ClassVar[bool] = False
    text_fields: ClassVar[tuple[str, ...]] = ("name", "brief")

    helper_type: str = "verifier"
    state: VerifierState = VerifierState.VERIFYING

    def next_judgement(self, brief: str) -> "Verifier":
        return self.with_(brief=brief, state=VerifierState.VERIFYING, pid=0)

    def running_as(self, pid: int) -> "Verifier":
        return self.with_(pid=pid)

    def judged(self) -> "Verifier":
        return self.with_(state=VerifierState.JUDGED, token_hash="")

    def exited(self) -> "Verifier":
        return self.with_(pid=0).with_event(VerifierExited(environment_id=self.environment_id))

    def ended(self) -> "Verifier":
        return self.with_(state=VerifierState.ENDED, token_hash="").exited() if self.is_verifying() else self.exited()

    def has_ended(self) -> bool:
        return self.state == VerifierState.ENDED

    def is_verifying(self) -> bool:
        return self.state == VerifierState.VERIFYING
