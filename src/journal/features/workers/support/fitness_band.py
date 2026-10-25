from journal.support.card_outcome import CardOutcome

DANGER_SCORE = 25
HEALTHY_SCORE = 75


class FitnessBand:
    """The colour a fitness score is shown in, the same everywhere: red under 25, a score far too low, orange under 75, green from 75 up."""

    @staticmethod
    def outcome(score: int) -> CardOutcome:
        if score < DANGER_SCORE:
            return CardOutcome.FAILED
        return CardOutcome.WARNED if score < HEALTHY_SCORE else CardOutcome.PASSED
