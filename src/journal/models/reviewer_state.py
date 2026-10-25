from enum import StrEnum


class ReviewerState(StrEnum):
    REVIEWING = "reviewing"
    REVIEWED = "reviewed"
    ENDED = "ended without a review"
