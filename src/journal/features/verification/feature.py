from journal.support.card_family import CardFamily
from journal.support.mark_kind import MarkKind
from journal.support.mark_kinds import JOURNAL
from journal.support.card_kind import CardKind
from journal.support.card_colouring import CardColouring
from journal.features.feature import Feature
from journal.features.verification.commands.verdict_command import VerdictCommand
from journal.features.verification.listeners.model_fit_sample import ModelFitSample
from journal.features.verification.listeners.verifier_card import VerifierCard
from journal.features.verification.listeners.verifier_retirement import VerifierRetirement
from journal.features.verification.listeners.typed_verdict import TypedVerdict
from journal.features.verification.listeners.verifier_start import VerifierStart
from journal.features.verification.states.verifying import Verifying
from journal.features.verification.verification_nudges import VerificationNudges
from journal.features.verification.support.verifier_process_card import VerifierProcessCard


class Verification(Feature):
    """An agent's dismissal of what the journal found is judged by a verifier the journal sends itself, never the agent: the verifier is an agent of its own, never a worker and unknown to the main agent, resting on Verifying from its first hook; it answers yes or no with one reason, and a no holds the agent's writes until the finding is fixed."""

    name = "verification"
    card_families = (CardFamily("verifiers", "Verifiers", "verifier", JOURNAL, CardColouring.OUTCOME),)
    card_kinds = (MarkKind(CardKind.VERIFIERS, "Dismissals a verifier checked", "verifiers", shown=False),)
    title = "Verifying dismissals"
    fixed = True
    help = "When the agent dismisses a reader report rather than fixing the reader, the journal sends a verifier that judges the dismissal on the evidence; on a no, the agent's writes wait until the reader is written anew."
    states = (Verifying,)
    process_cards = (VerifierProcessCard,)
    commands = (VerdictCommand,)
    listeners = (VerifierStart, VerifierCard, VerifierRetirement, ModelFitSample, TypedVerdict)
    nudges = (VerificationNudges.VERIFIER_REFUSAL,)
