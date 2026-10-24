from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.models.message import Message
from journal.models.reader_report import ReaderReport
from journal.models.support.ref import Ref
from journal.models.verifier import Verifier
from journal.models.verifier_state import VerifierState
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class VerifierProcessCard(ProcessCard):
    """A verifier's one card in the chat, for the person and never the main agent: judging the dismissal of a reader report while it runs, then the verdict with its reason, or that it ended without one."""

    name = "verifier"

    def card_contents(self, verifier: Verifier, report: ReaderReport) -> ProcessCardContents:
        tone, text = self.standing(verifier, report)
        data = {"kind": "card", "icon": "verifier", "tone": tone, "row": str(Ref.build(report))}
        detail = report.verdict if verifier.state == VerifierState.JUDGED else ""
        return ProcessCardContents(self.name, verifier.environment_id, f"verifier:{verifier.id}", f"Verifier {verifier.id}, {verifier.name}: {text}", data, Actor.system(), CardKind.VERIFIERS, verifier.is_verifying(), detail)

    @staticmethod
    def standing(verifier: Verifier, report: ReaderReport) -> tuple[str, str]:
        if verifier.state == VerifierState.VERIFYING:
            return "", f"judging the dismissal of reader report {report.id}"
        if verifier.state == VerifierState.ENDED:
            return "bad", f"ended without a verdict on reader report {report.id}"
        return ("bad", "the dismissal is refuted") if report.is_refuted else ("good", "the dismissal is sound")

    def refresh(self, message: Message) -> dict:
        return {}
