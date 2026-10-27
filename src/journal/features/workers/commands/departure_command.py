import shlex
from argparse import Namespace
from pathlib import Path

from journal.console.command import Command
from journal.engine.command_events import CommandEvents
from journal.events.worker_clocking_out import WorkerClockingOut
from journal.events.worker_delivering import WorkerDelivering
from journal.events.worker_merging import WorkerMerging
from journal.features.plugins.plugins_options import PluginsOptions
from journal.support.time_source import TimeSource
from journal.features.workers.support.worker_branch import REBASE_STEPS, WorkerBranch
from journal.features.workers.support.pool_worker_moves import DELIVERED, PoolWorkerMoves
from journal.features.workers.support.affected_tests import AffectedTests
from journal.features.workers.support.test_selection import TestSelection
from journal.features.workers.support.test_turns import TestTurns
from journal.features.workers.support.worker_reports import WorkerReports
from journal.features.workers.workers_options import JOURNAL_TESTING, WorkersOptions
from journal.models.task_log import TaskLog
from journal.models.test_outcome import TestOutcome
from journal.models.proof_state import ProofState
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.features.workers.support.worker_task_assigner import WorkerTaskAssigner
from journal.repositories.proofs import Proofs
from journal.repositories.setting_rows import SettingRows
from journal.repositories.task_logs import TaskLogs
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection


TESTING_HELD = "your clock-out was held by a plugin before the journal rebased your work and ran your tests; fix what it found, then clock out again"
DELIVERY_HELD = "your tests passed, but a plugin held your work before it reaches the agent that sent you; fix what it found, then clock out again, and the journal runs your tests again"

class DepartureCommand(Command):
    """journal clock-out "<report>": a worker's one report, accepted only once every point of its task's brief has a valid proof, its worktree has no uncommitted file and its branch has been moved up to the branch its work merges into, a clash there sent back to it at once with the files that clash, and, while the journal runs the tests, the tests it names have passed in its worktree, a failing run sent back to it at once with its failing lines. A worker on a queue whose report choice is not yet due finishes the task instead, which waits for the merge with the rest, and goes straight on to its next queued task in the same session, its report kept for later; a pool worker does the same on its teammate's machine, and pushes its branch to origin at every clock-out so the merge sees each finished task. A worker goes on to its next task while its report is not due, no point of this one is proved not done and the next is not blocked; a blocked task next in the queue stops it too, and a point proved not done stops the queue so the worker reports at once."""

    noun = "clock-out"
    default_verb = "record"

    def __init__(self, workers: Workers, tasks: Tasks, proofs: Proofs, reports: WorkerReports, branch: WorkerBranch, moves: PoolWorkerMoves, turns: TestTurns, settings: SettingRows, logs: TaskLogs, events: CommandEvents, time_source: TimeSource, affected: AffectedTests, assigner: WorkerTaskAssigner) -> None:
        self.assigner = assigner
        self.workers, self.tasks, self.proofs, self.reports, self.branch, self.moves = workers, tasks, proofs, reports, branch, moves
        self.turns, self.settings, self.logs, self.events, self.time_source, self.affected = turns, settings, logs, events, time_source, affected

    def arguments(self, verbs) -> None:
        record = self.verb(verbs, "record", "hand in your work with your report, once each point of your brief has a proof")
        record.add_argument("report")
        record.add_argument("--tests", default="", help="the arguments the project's test command takes to run the tests that cover the files you changed and the tests you wrote, never the whole suite; the journal runs them before your clock-out stands")

    def record(self, args: Namespace, caller: Caller) -> int:
        if caller.worker_number is None:
            raise Rejection("only a worker clocks out: a worker's commands carry its number")
        worker = self.workers.find(caller.worker_number)
        holdings = self.tasks.holder_task_ids(Ref(Worker.table(), worker.id))
        if not holdings:
            raise Rejection(f"worker {worker.id} has no task: a worker clocks out of the task it was sent on")
        task = self.tasks.find(holdings[0])
        missing = self.unproved(task)
        if missing:
            raise Rejection(f"point {', '.join(map(str, missing))} of task {task.id} has no proof: `journal proof <point> \"<file:line and test>\"`")
        start_heads = self.branch.worktree_heads(worker)
        self.branch.commit_changes(worker, f"Task {task.id}: {task.title}")
        self.plugin_check(WorkerClockingOut, worker, task, TESTING_HELD)
        clashing = self.clashing(worker)
        if clashing:
            raise Rejection(f"your work, rebased onto {self.branch.project_heads(worker)}, clashes: {clashing}; {REBASE_STEPS}, then clock out")
        uncommitted = self.branch.uncommitted_files(worker) if worker.worktree else []
        if uncommitted:
            raise Rejection(f"still not committed after the journal's commit: {', '.join(uncommitted)}; check git status, fix it and clock out")
        strays = self.branch.other_repository_folders(worker) if worker.worktree else []
        if strays:
            raise Rejection(f"your worktree has folders outside your task's repositories, which would be lost: {', '.join(strays)}; move or remove them")
        lying = self.branch.branch_untracked_files(worker) if worker.worktree else []
        if lying:
            raise Rejection(f"your branch adds {', '.join(lying)}, untracked in the project: git rm --cached them, commit, clock out again")
        if self.branch.worktree_heads(worker) != start_heads:
            print(f"the journal committed your work and rebased it onto the project's branch, at {self.branch.project_heads(worker)}")
        if worker.rebase_due:
            self.workers.save(self.workers.find(worker.id).rebased(f"its worktree rebased onto the project's branch at its clock-out, at {self.branch.project_heads(worker)}", self.time_source.moment().timestamp()), caller.actor)
        if self.is_journal_testing(worker):
            self.tested(worker, task, args.tests, caller)
        self.plugin_check(WorkerDelivering, worker, task, DELIVERY_HELD)
        holder = Ref(Worker.table(), worker.id)
        waiting = self.tasks.queue(holder)
        following = self.assigner.following(worker)
        if worker.pool_request:
            self.push_branch(worker)
        if following is not None and self.continues_queue(worker, task, waiting):
            return self.advance_queue(worker, task, following, caller)
        if worker.pool_request:
            self.moves.ended(worker)
        if self.moves.is_remote(worker):
            self.moves.ask(worker, DELIVERED, {"report": args.report}, caller.actor)
        else:
            self.reports.delivered(worker, args.report, caller.actor)
        print(f"worker {worker.id} clocked out of task {task.id}; the agent that sent you checks each proof")
        return 0

    def plugin_check(self, event_class: type[WorkerMerging], worker: Worker, task: Task, refusal_heading: str) -> None:
        if not worker.worktree or worker.pool_request:
            return
        refusals = self.events.worker_merging(self.branch.merging_event(event_class, worker, task.id, self.settings.integer(PluginsOptions.CLOCK_OUT_WINDOW_SECONDS) * 1000))
        if refusals:
            raise Rejection(refusal_heading + "\n" + "\n".join(refusals))

    def is_journal_testing(self, worker: Worker) -> bool:
        return not worker.pool_request and self.settings.option(WorkersOptions.TESTING) == JOURNAL_TESTING

    def tested(self, worker: Worker, task: Task, tests: str, caller: Caller) -> None:
        folder = self.branch.folder(worker)
        if not TestSelection.parsed(tests).names_tests(folder):
            raise Rejection(f"name the tests for {', '.join(self.branch.touched(worker) or ()) or 'your changes'}: journal clock-out \"<report>\" --tests \"<args>\"")
        turn, run_lines = self.turns.checked(worker, self.with_affected(worker, tests.strip(), folder), caller)
        if turn.outcome != TestOutcome.PASSED:
            raise Rejection(f"your tests did not pass, so your clock-out does not stand: fix them and clock out again\n{run_lines}")
        self.logs.save(TaskLog.build(task, f"tests passed at clock-out: {turn.command}", self.time_source.moment().timestamp()), caller.actor)

    def with_affected(self, worker: Worker, tests: str, folder: Path) -> str:
        missing = TestSelection.parsed(tests).missing(self.affected.selection(worker))
        if not missing:
            return tests
        print(f"the journal runs the tests that cover your changes and that you did not name too: {' '.join(missing)}")
        return f"{tests} && {self.turns.command(str(folder))} {shlex.join(missing)}"

    def continues_queue(self, worker: Worker, task: Task, waiting: list[Task]) -> bool:
        finished = len(self.tasks.finished_task_ids(Ref(Worker.table(), worker.id)))
        return not (self.is_unfinished(task) or self.is_blocked(waiting) or worker.report_choice.is_report_due(finished, len(waiting)))

    def advance_queue(self, worker: Worker, task: Task, following: Task, caller: Caller) -> int:
        self.tasks.finish_holder_task(task.id, Ref(Worker.table(), worker.id), caller.actor)
        next_task = self.assigner.handed(worker, following, caller.actor)
        self.workers.save(self.workers.find(worker.id).queue_advanced(next_task.id, self.time_source.moment().timestamp()), caller.actor)
        print(f"task {task.id} is done and waits to be checked and merged with the rest of your queue; your next task, {next_task.id}: {next_task.title}. {next_task.brief}")
        print("work on it now in this session: prove each of its points and clock out again; the journal commits your work")
        return 0

    def push_branch(self, worker: Worker) -> None:
        outcome = self.branch.git("push", "origin", f"{self.branch.name(worker)}:refs/heads/{WorkerBranch.pool_branch(worker)}", cwd=self.branch.folder(worker))
        if outcome.returncode != 0:
            raise Rejection(f"your branch could not be pushed to origin for the agent that sent you: {outcome.stderr.strip()}; fix it and clock out again")

    @staticmethod
    def is_blocked(waiting: list[Task]) -> bool:
        return bool(waiting) and waiting[0].state == TaskState.BLOCKED

    def is_unfinished(self, task: Task) -> bool:
        latest = {proof.point: proof for proof in sorted(self.proofs.task_proofs(task), key=lambda proof: proof.row_id)}
        return any(proof.state == ProofState.UNFINISHED for proof in latest.values())

    def unproved(self, task: Task) -> list[int]:
        latest = {proof.point: proof for proof in sorted(self.proofs.task_proofs(task), key=lambda proof: proof.row_id)}
        return [point for point in range(1, len(task.points()) + 1) if point not in latest or latest[point].state in (ProofState.SHORT, ProofState.STALE)]

    def clashing(self, worker: Worker) -> str:
        return "" if worker.pool_request else self.branch.rebased_onto_branch(worker)

