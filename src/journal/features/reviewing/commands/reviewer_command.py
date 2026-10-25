from argparse import Namespace

from journal.console.command import Command
from journal.features.reviewing.support.review_queue import ReviewQueue
from journal.features.reviewing.support.review_routing import ReviewRouting
from journal.features.reviewing.support.reviewer_dispatch import ReviewerDispatch
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.reviewers import Reviewers
from journal.repositories.setting_rows import SettingRows
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class ReviewerCommand(Command):
    """journal reviewer add|retire|list: the reviewers the journal hands the review queue to, in orchestrator mode with the reviewer on. add starts another, which takes the next review in the queue at once; retire lets an idle one go; list names each reviewer and the reviews waiting, in their order."""

    noun = "reviewer"
    default_verb = "list"

    def __init__(self, reviewers: Reviewers, workers: Workers, dispatch: ReviewerDispatch, queue: ReviewQueue, routing: ReviewRouting, scope: Scope, settings: SettingRows) -> None:
        self.reviewers, self.workers, self.dispatch, self.queue, self.routing, self.scope, self.settings = reviewers, workers, dispatch, queue, routing, scope, settings

    def arguments(self, verbs) -> None:
        self.verb(verbs, "add", "start another reviewer, which takes the next review waiting at once")
        self.verb(verbs, "retire", "let an idle reviewer go")
        self.verb(verbs, "list", "the reviewers and the reviews waiting for one")

    def add(self, args: Namespace, caller: Caller) -> int:
        if not self.routing.is_enabled():
            raise Rejection("the reviewer is off: turn the Reviewer switch on, in orchestrator mode, first")
        limit = self.settings.integer(WorkersOptions.REVIEWER_LIMIT)
        if len(self.reviewers.active()) >= limit:
            raise Rejection(f"{limit} reviewers are out, the limit workers.reviewers_most sets; {self.standing()}")
        added = self.dispatch.added(self.scope.id)
        self.queue.assigned(self.scope.id)
        print(f"reviewer {added.id} added; {self.standing()}")
        return 0

    def retire(self, args: Namespace, caller: Caller) -> int:
        idle = self.reviewers.idle()
        if not idle:
            raise Rejection(f"no reviewer is idle: each is reviewing; {self.standing()}")
        self.reviewers.save(idle[-1].retired(), caller.actor)
        print(f"reviewer {idle[-1].id} retired; {self.standing()}")
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        for reviewer in self.reviewers.active():
            print(f"reviewer {reviewer.id}, {reviewer.name}: {reviewer.state}")
        for place, worker in enumerate(self.workers.queued_reviews(), 1):
            print(f"waiting {place}: worker {worker.id}, {worker.name}")
        print(self.standing())
        return 0

    def standing(self) -> str:
        return f"reviewers: {len(self.reviewers.active())}, reviews waiting: {len(self.workers.queued_reviews())}"
