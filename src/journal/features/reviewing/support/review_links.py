from journal.models.link import Link
from journal.models.reviewer import Reviewer
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.links import Links
from journal.support.actor import Actor
from journal.support.rejection import Rejection

REVIEWS = "reviews"


class ReviewLinks:
    """The link from a reviewer to each worker whose work it reviews: made as a review starts, and read for the worker it reviews now, the last it was linked to."""

    def __init__(self, links: Links) -> None:
        self.links = links

    def linked(self, reviewer: Reviewer, worker: Worker) -> None:
        self.links.save(Link(source=Ref.build(reviewer), target=Ref.build(worker), link_type=REVIEWS), Actor.system())

    def worker(self, reviewer: Reviewer) -> Ref:
        targets = self.links.targets(reviewer, REVIEWS)
        if not targets:
            raise Rejection(f"reviewer {reviewer.id} reviews nothing: only a reviewer the journal sent gives a review")
        return targets[-1]
