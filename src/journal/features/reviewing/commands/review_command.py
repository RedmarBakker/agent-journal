from argparse import Namespace
from datetime import datetime, timezone

from journal.console.command import Command
from journal.features.reviewing.support.review_links import ReviewLinks
from journal.features.reviewing.support.review_report import ReviewReport
from journal.features.reviewing.support.review_sign_off import ReviewSignOff
from journal.models.reviewer import Reviewer
from journal.models.worker import Worker
from journal.support.actor import Actor
from journal.models.author import Author
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.repositories.messages import Messages
from journal.repositories.reviewers import Reviewers
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


class ReviewCommand(Command):
    """journal review "<report>": a reviewer's one report on the worker's work it reviews, one line per point, passed, short with why, or undecided with why. With every point passed it signs the work off, which merges it and sends the worker on to its next queued task; a point short goes back to the worker with the reason; a point undecided or not named leaves the work to the agent that sent the worker. It is in the chat, shown point by point in the reviewer pane, and ends the reviewer's session."""

    noun = "review"
    default_verb = "record"

    def __init__(self, links: ReviewLinks, reviewers: Reviewers, workers: Workers, tasks: Tasks, messages: Messages, sign_off: ReviewSignOff, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.links, self.reviewers, self.workers, self.tasks, self.messages, self.sign_off = links, reviewers, workers, tasks, messages, sign_off

    def arguments(self, verbs) -> None:
        self.verb(verbs, "record", "your report on the work you review: one line per point, passed, short with why and the failing output, or undecided with why").add_argument("report")

    def record(self, args: Namespace, caller: Caller) -> int:
        if not caller.is_reviewer():
            raise Rejection("only a reviewer the journal sent gives a review")
        reviewer = self.reviewers.find(caller.reviewer_number)
        worker = self.workers.find(self.links.worker(reviewer).id)
        task = self.tasks.last_task_id(Ref.build(worker))
        report = ReviewReport(args.report)
        self.messages.save(Message(environment_id=worker.environment_id, author=Author.AGENT, text=f"{reviewer.name} reports: worker {worker.id}, {worker.name}, on task {task}: {args.report}", data={"kind": Message.REPORT, "worker": reviewer.name, "reviewer_id": reviewer.id}), caller.actor)
        outcome = self.undecided(reviewer, worker, task, report, caller.actor) if report.is_undecided(len(self.tasks.find(task).points())) else self.decided(reviewer, worker, task, report, caller.actor)
        print(f"review of worker {worker.id} on task {task} given: {outcome}; your session ends now")
        return 0

    def undecided(self, reviewer: Reviewer, worker: Worker, task: int, report: ReviewReport, actor: Actor) -> str:
        self.workers.save(worker.review_undecided(self.time_source.moment().timestamp(), task, reviewer, report.text), actor)
        return "a point is undecided or not named, so the agent that sent the worker decides"

    def decided(self, reviewer: Reviewer, worker: Worker, task: int, report: ReviewReport, actor: Actor) -> str:
        self.workers.save(worker.reviewed(self.time_source.moment().timestamp(), task, reviewer, report.text), actor)
        return self.sign_off.applied(worker.id, report, actor)
