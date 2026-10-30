from argparse import Namespace

from journal.console.command import Command
from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.support.worker_reports import WorkerReports
from journal.models.support.ref import Ref
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class WorkerPeerCommand(Command):
    """journal worker as a worker runs it: a report for itself, a job or a word to another worker of the agent that dispatched it, and the list of those workers."""

    noun = "worker"

    def __init__(self, workers: Workers, reports: WorkerReports, branch: WorkerBranch, actions: WorkerActions, tasks: Tasks) -> None:
        self.workers, self.reports, self.branch, self.actions, self.tasks = workers, reports, branch, actions, tasks

    def arguments(self, verbs) -> None:
        report = self.verb(verbs, "report", "the worker reports back")
        report.add_argument("n", type=int)
        report.add_argument("text")
        line = self.verb(verbs, "send", "give another worker of your dispatcher that reported or was stopped its next job")
        line.add_argument("n", type=int)
        line.add_argument("brief")
        line.add_argument("--task", type=int, help="the task this job works on")
        line.add_argument("--model", help="refused: only the dispatcher changes a worker's model")
        line.add_argument("--profile", help="refused: only the dispatcher changes a worker's profile")
        notify = self.verb(verbs, "notify", "give another running worker of your dispatcher a message in its live session")
        notify.add_argument("n", type=int)
        notify.add_argument("text")
        self.verb(verbs, "peers", "the other workers of the agent that dispatched you, out or idle, and what each is on")

    def report(self, args: Namespace, caller: Caller) -> int:
        if caller.worker_number != args.n:
            raise Rejection(f"worker {args.n} is not you: a worker reports for itself, worker {caller.worker_number}")
        worker = self.workers.find(args.n)
        if worker.token_hash:
            raise Rejection("a worker reports by clocking out: journal clock-out \"<report>\", once each point of its brief has a proof")
        message = self.reports.file(worker.with_(session=worker.session if caller.session is None else caller.session, touched_paths=self.branch.touched(worker)), args.text, caller.actor)
        print(f"worker {worker.id} reported in message {message.id}")
        return 0

    def send(self, args: Namespace, caller: Caller) -> int:
        if args.model or args.profile:
            raise Rejection("only the agent that dispatched a worker changes its model or its profile")
        self.actions.task_holdings(args.n, args.task)
        if args.task:
            task, worker = self.tasks.find(args.task), self.workers.find(args.n)
            self.tasks.guard_worker_task(task, Ref.build(worker), caller.actor)
            self.tasks.require_assignment_ready(task)
        worker = self.actions.peer_send(args.n, args.brief, caller.worker_number, caller.actor)
        if args.task:
            self.tasks.handover(self.tasks.find(args.task), Ref.build(worker), caller.actor)
        print(f"worker {worker.id} {worker.name} told, on {worker.model}; it reports in the chat when it ends")
        return 0

    def notify(self, args: Namespace, caller: Caller) -> int:
        worker = self.actions.peer_notify(args.n, args.text, caller.worker_number, caller.actor)
        print(f"worker {worker.id} {worker.name} has the message in its session")
        return 0

    def peers(self, args: Namespace, caller: Caller) -> int:
        peers = self.workers.peers(self.workers.find(caller.worker_number))
        for worker in peers:
            print(f"{worker.id:>4}  {'out' if worker.is_running() else 'idle':<5} {worker.name}: {worker.brief}")
        print(f"`journal worker notify <n> \"<text>\"` tells one that is out, `journal worker send <n> \"<job>\"` gives one that is idle a job" if peers else "no other worker of the agent that dispatched you is out or idle")
        return 0
