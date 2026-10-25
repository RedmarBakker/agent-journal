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
from journal.support.card_kind import CardKind


class VerifierProcessCard(ProcessCard):
    """A verifier's one card in the chat, for the person and never the main agent: judging the dismissal of a reader report, or whether a merged worker's model fit its work, while it runs, then the verdict with its reason, or that it ended without one."""

    name = "verifier"

    def card_contents(self, verifier: Verifier, report: ReaderReport) -> ProcessCardContents:
        tone, text = self.standing(verifier, report)
        return self.contents(verifier, report, tone, text, report.verdict if verifier.state == VerifierState.JUDGED else "")

    def fit_card_contents(self, verifier: Verifier, worker: Worker) -> ProcessCardContents:
        tone, text = self.fit_standing(verifier, worker)
        return self.contents(verifier, worker, tone, text, worker.model_fit.reason if verifier.state == VerifierState.JUDGED else "")

    def contents(self, verifier: Verifier, row: Scoped, tone: str, text: str, detail: str) -> ProcessCardContents:
        data = {"kind": "card", "icon": "verifier", "tone": tone, "row": str(Ref.build(row))}
        return ProcessCardContents(self.name, verifier.environment_id, f"verifier:{verifier.id}", f"Verifier {verifier.id}, {verifier.name}: {text}", data, Actor.system(), CardKind.VERIFIERS, verifier.is_verifying(), detail)

    @staticmethod
    def standing(verifier: Verifier, report: ReaderReport) -> tuple[str, str]:
        if verifier.state == VerifierState.VERIFYING:
            return "", f"judging the dismissal of reader report {report.id}"
        if verifier.state == VerifierState.ENDED:
            return "bad", f"ended without a verdict on reader report {report.id}"
        return ("bad", "the dismissal is refuted") if report.is_refuted else ("good", "the dismissal is sound")

    @staticmethod
    def fit_standing(verifier: Verifier, worker: Worker) -> tuple[str, str]:
        if verifier.state == VerifierState.VERIFYING:
            return "", f"judging whether worker {worker.id}'s model fit its work"
        if verifier.state == VerifierState.ENDED:
            return "bad", f"ended without a verdict on worker {worker.id}'s model"
        return ("good", f"worker {worker.id}'s model was right") if worker.model_fit.verdict == RIGHT else ("bad", f"worker {worker.id}'s model was {worker.model_fit.verdict}")

    def refresh(self, message: Message) -> dict:
        return {}
