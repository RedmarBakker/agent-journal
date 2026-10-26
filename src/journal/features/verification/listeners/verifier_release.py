from journal.events.listener import Listener
from journal.events.rows.verifier_exited import VerifierExited
from journal.features.verification.support.verifier_dispatch import VerifierDispatch


class VerifierRelease(Listener[VerifierExited]):
    """A verifier whose process ended takes the next judgement waiting."""

    def __init__(self, dispatch: VerifierDispatch) -> None:
        self.dispatch = dispatch

    def handle(self, event: VerifierExited) -> None:
        self.dispatch.released()
