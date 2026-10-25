from argparse import Namespace
from datetime import datetime, timezone

from journal.console.command import REVIEWER_KINDS, Command
from journal.features.reviewing.support.reviewer_dispatch import ReviewerDispatch
from journal.models.author import Author
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.repositories.messages import Messages
from journal.repositories.reviewers import Reviewers
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class ReviewCommand(Command):
    """journal review "<report>": a reviewer's one report on the worker's work it reviews, one short line per point, passed or short with why, and the tests it ran; it reaches the agent that sent the worker, in the chat too, and ends the reviewer's session."""

    noun = "review"
    default_verb = "record"
    callers = {"record": REVIEWER_KINDS}

    def __init__(self, dispatch: ReviewerDispatch, reviewers: Reviewers, workers: Workers, tasks: Tasks, messages: Messages) -> None:
        self.dispatch, self.reviewers, self.workers, self.tasks, self.messages = dispatch, reviewers, workers, tasks, messages

    def arguments(self, verbs) -> None:
        self.verb(verbs, "record", "your report on the work you review: one short line per point, passed or short with why, and the tests you ran").add_argument("report")

    def record(self, args: Namespace, caller: Caller) -> int:
        if caller.reviewer_number is None:
            raise Rejection("only a reviewer the journal sent gives a review")
        reviewer = self.reviewers.find(caller.reviewer_number)
        worker = self.workers.find(self.dispatch.reviewed(reviewer.id).id)
        task = self.tasks.last_task_id(Ref.build(worker))
        self.workers.save(worker.reviewed(datetime.now(timezone.utc).timestamp(), task, reviewer, args.report), caller.actor)
        self.messages.save(Message(environment_id=worker.environment_id, author=Author.AGENT, text=f"{reviewer.name} reports: worker {worker.id}, {worker.name}, on task {task}: {args.report}", data={"kind": Message.REPORT, "worker": reviewer.name, "reviewer_id": reviewer.id}), caller.actor)
        print(f"review of worker {worker.id} on task {task} given; the agent that sent it decides, and your session ends now")
        return 0
