from journal.models.link import Link
from journal.models.reviewer import Reviewer
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.links import Links
from journal.support.actor import Actor
from journal.support.rejection import Rejection

REVIEWS = "reviews"
REVIEW_TASKS = "review_tasks"


class ReviewLinks:
    """The links from each reviewer to the worker and task assigned to its current review."""

    def __init__(self, links: Links) -> None:
        self.links = links

    def linked(self, reviewer: Reviewer, worker: Worker, task: Task) -> None:
        self.links.save(Link(source=Ref.build(reviewer), target=Ref.build(worker), link_type=REVIEWS), Actor.system())
        self.links.save(Link(source=Ref.build(reviewer), target=Ref.build(task), link_type=REVIEW_TASKS), Actor.system())

    def worker(self, reviewer: Reviewer) -> Ref:
        targets = self.links.targets(reviewer, REVIEWS)
        if not targets:
            raise Rejection(f"reviewer {reviewer.id} reviews nothing: only a reviewer the journal sent gives a review")
        return targets[-1]

    def task(self, reviewer: Reviewer) -> Ref:
        targets = self.links.targets(reviewer, REVIEW_TASKS)
        if not targets:
            raise Rejection(f"reviewer {reviewer.id} reviews no task: only a reviewer the journal sent gives a review")
        return targets[-1]
