from journal.models.verifier import Verifier
from journal.models.verifier_state import VerifierState
from journal.repositories.checkers import Checkers


class Verifiers(Checkers[Verifier]):
    model = Verifier

    def out(self) -> list[Verifier]:
        return self.selected(self.query().filter_listed("state", [VerifierState.VERIFYING, VerifierState.JUDGED]).order("id"))

    def idle(self) -> list[Verifier]:
        return self.newest(self.query().filter(state=VerifierState.JUDGED).limit(1))
