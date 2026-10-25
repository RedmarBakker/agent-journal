from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewingData:
    """The reviewing feature's reading: how many reviews wait in the queue for a reviewer, and how many reviewers there are."""

    waiting_reviews: int
    reviewers: int
