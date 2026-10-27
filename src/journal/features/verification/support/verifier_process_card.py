from journal.support.card_outcome import CardOutcome
from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.models.message import Message
from journal.models.reader_report import ReaderReport
from journal.models.scoped import Scoped
from journal.models.support.model_fit import RIGHT
from journal.models.worker import Worker
from journal.models.support.ref import Ref
from journal.models.verifier import Verifier
from journal.models.verifier_state import VerifierState
from journal.support.actor import Actor
from journal.support.card_type import CardType


class VerifierProcessCard(ProcessCard):
    """A verifier's one card in the chat, for the person and never the main agent: judging the dismissal of a reader report, or whether a merged worker's model fit its work, while it runs, then the verdict with its reason, or that it ended without one."""

    name = "verifier"

    def card_contents(self, verifier: Verifier, report: ReaderReport) -> ProcessCardContents:
        outcome, text = self.standing(verifier, report)
        return self.contents(verifier, report, outcome, text, report.verdict if verifier.state == VerifierState.JUDGED else "")

    def fit_card_contents(self, verifier: Verifier, worker: Worker) -> ProcessCardContents:
        outcome, text = self.fit_standing(verifier, worker)
        return self.contents(verifier, worker, outcome, text, worker.model_fit.reason if verifier.state == VerifierState.JUDGED else "")

    def contents(self, verifier: Verifier, row: Scoped, outcome: CardOutcome, text: str, detail: str) -> ProcessCardContents:
        data = {"kind": "card", "outcome": str(outcome), "row": str(Ref.build(row))}
        return ProcessCardContents(self.name, verifier.environment_id, f"verifier:{verifier.id}", f"{verifier.name}: {text}", data, Actor.system(), CardType.VERIFIERS, verifier.is_verifying(), detail)

    @staticmethod
    def standing(verifier: Verifier, report: ReaderReport) -> tuple[CardOutcome, str]:
        if verifier.state == VerifierState.VERIFYING:
            return CardOutcome.RUNNING, "checking whether a dismissed report was right"
        if verifier.state == VerifierState.ENDED:
            return CardOutcome.FAILED, "stopped before reaching a conclusion"
        return (CardOutcome.FAILED, "the report was right after all") if report.is_refuted else (CardOutcome.PASSED, "the report was rightly dismissed")

    @staticmethod
    def fit_standing(verifier: Verifier, worker: Worker) -> tuple[CardOutcome, str]:
        if verifier.state == VerifierState.VERIFYING:
            return CardOutcome.RUNNING, f"checking whether {worker.name}'s model fit its work"
        if verifier.state == VerifierState.ENDED:
            return CardOutcome.FAILED, "stopped before reaching a conclusion"
        return (CardOutcome.PASSED, f"{worker.name}'s model was right") if worker.model_fit.verdict == RIGHT else (CardOutcome.FAILED, f"{worker.name}'s model was {worker.model_fit.verdict}")

    def refresh(self, message: Message) -> dict:
        return {}
