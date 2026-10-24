from enum import StrEnum


class VerifierState(StrEnum):
    VERIFYING = "verifying"
    JUDGED = "judged"
    ENDED = "ended without a verdict"
