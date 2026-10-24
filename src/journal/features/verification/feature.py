from journal.features.feature import Feature
from journal.features.verification.commands.verdict_command import VerdictCommand
from journal.features.verification.listeners.verifier_end import VerifierEnd
from journal.features.verification.listeners.verifier_start import VerifierStart
from journal.features.verification.states.verifying import Verifying
from journal.features.verification.verification_nudges import VerificationNudges
from journal.features.verification.verifier_conduct import VerifierConduct


class Verification(Feature):
    """An agent's dismissal of what the journal found is judged by a verifier the journal sends itself, never the agent: the verifier is held in Verifying, answers yes or no with one reason, and a no holds the agent's writes until the finding is fixed."""

    name = "verification"
    title = "Verifying dismissals"
    fixed = True
    help = "When the agent dismisses a reader report rather than fixing the reader, the journal sends a verifier that judges the dismissal on the evidence; on a no, the agent's writes wait until the reader is written anew."
    states = (Verifying,)
    verifier_conduct = (VerifierConduct,)
    commands = (VerdictCommand,)
    listeners = (VerifierStart, VerifierEnd)
    nudges = (VerificationNudges.VERIFIER_REFUSAL,)
