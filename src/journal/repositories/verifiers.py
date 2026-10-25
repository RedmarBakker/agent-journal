from journal.models.verifier import Verifier
from journal.models.verifier_state import VerifierState
from journal.repositories.checkers import Checkers


class Verifiers(Checkers[Verifier]):
    model = Verifier

    def idle(self) -> list[Verifier]:
        return self.newest(self.query().filter(state=VerifierState.JUDGED).limit(1))
