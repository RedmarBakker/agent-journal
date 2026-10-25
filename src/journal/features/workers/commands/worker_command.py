import time
from datetime import datetime, timezone
from journal.features.team.support.start_rule import StartRule
from journal.providers.support.profile_kind import ProfileKind
from journal.chat.card_detail import CardDetail
from argparse import Namespace

from journal.repositories.setting_rows import SettingRows
from journal.features.tasks.active_task import ActiveTask
from journal.features.workers.support.merge_checks import MergeChecks
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.support.worktree_failure import WorktreeFailure
from journal.console.command import WORKER_KINDS, Command
from journal.support.caller import Caller
from journal.features.profiles.support.profile_files import ProfileFiles
from journal.features.workers.support.worker_reports import WorkerReports
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.features.workers.support.worker_launch import WorkerLaunch
from journal.models.worker import Worker
from journal.providers.providers import Providers
from journal.support.rejection import Rejection
from journal.features.workers.support.merge_steps import MergeSteps
from journal.features.workers.support.report_fitting import ReportFitting
from journal.models.support.report_choice import POOL_REFUSAL, ReportChoice
from journal.repositories.messages import Messages
from journal.repositories.scope import Scope
from journal.repositories.subagents import Subagents
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.agents import Agents
from journal.models.worker_state import WorkerState
from journal.models.template import Template
from journal.repositories.tasks import Tasks
from journal.repositories.plans import Plans
from journal.repositories.workers import Workers
from journal.repositories.templates import Templates
from journal.features.workers.support.worker_actions import WorkerActions
from journal.engine.command_events import CommandEvents
from journal.features.tasks.support.wait_targets import WaitTargets
from journal.features.workers.support.worker_libraries import WorkerLibraries
from journal.features.workers.support.pool_dispatch import PoolDispatch
from journal.sync.team_account import TeamAccount
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import JOURNAL_TESTING, MERGER_TESTING, TEST_BUDGET, WorkersOptions
from journal.features.workers.workers_profiles import WorkersProfiles
from journal.features.templates.shipped import BUDGET_TESTS, JOURNAL_TESTS, SCOPED_TESTS, ZERO_TESTS

EMPTY_BRIEF_REFUSAL = "task {n} has no brief: a worker's job is its task's brief, so write it first with journal task brief {n} \"<what is done when>\""
ASSIGNMENT_REFUSALS = {
    TaskState.FINISHED: "task {n} is {state}: a worker is started only on an open task or one you hold",
    TaskState.CANCELLED: "task {n} is {state}: a worker is started only on an open task or one you hold",
    TaskState.BLOCKED: "task {n} is {state}: unblock it before a worker takes it",
    TaskState.STARTED: "task {n} is started in another's hands: a worker is started only on an open task or one you hold",
    TaskState.PAUSED: "task {n} is {state} in another's hands: a worker is started only on an open task or one you hold",
    TaskState.DELEGATED: "task {n} is delegated to a worker already: send that worker the next job, or release it first",
}

EMPTY_CHANGES = ("", "none", "nothing", "no files", "n/a", "-", "read only", "read-only", "nothing, it only reads")

TEST_COMMAND_MISSING = "the journal runs each worker's tests with the project's test command, and none is set: set it with journal tests command \"<the command, without the tests>\" --proof \"<the arguments that run one test that passes>\", then dispatch again"

class WorkerCommand(Command):
    noun = "worker"
    background_verbs = frozenset({"merge"})
    callers = {"peers": WORKER_KINDS, "notify": WORKER_KINDS, "send": WORKER_KINDS, "report": WORKER_KINDS}

    def __init__(self, workers: Workers, messages: Messages, runner: WorkerRunner, reports: WorkerReports, scope: Scope, profiles: ProfileFiles, providers: Providers, branch: WorkerBranch, settings: SettingRows, actions: WorkerActions, subagents: Subagents, tasks: Tasks, agents: Agents, events: CommandEvents, libraries: WorkerLibraries, plans: Plans, templates: Templates, starts: StartRule, pool: PoolDispatch, account: TeamAccount, launch: WorkerLaunch, checks: MergeChecks, taking: ActiveTask, targets: WaitTargets, fitting: ReportFitting) -> None:
        self.targets, self.fitting = targets, fitting
        self.launch, self.checks, self.taking = launch, checks, taking
        self.tasks, self.agents, self.events, self.libraries, self.plans, self.templates, self.starts = tasks, agents, events, libraries, plans, templates, starts
        self.workers, self.messages, self.providers = workers, messages, providers
        self.branch, self.settings, self.actions, self.subagents = branch, settings, actions, subagents
        self.runner, self.reports, self.scope, self.profiles = runner, reports, scope, profiles
        self.pool, self.account = pool, account

    def arguments(self, verbs) -> None:
        dispatch = self.verb(verbs, "dispatch", "send a worker to write one bounded job")
        dispatch.add_argument("name")
        dispatch.add_argument("brief", nargs="?", default="", help="what the worker is told beside its task's brief")
        dispatch.add_argument("--provider", choices=("claude", "codex"), help="the program the worker runs; the dispatching agent's own when not named")
        dispatch.add_argument("--changes", required=True, help="the files, folders or document the worker changes; a job that only reads, searches or reviews goes to a subagent, never a worker")
        dispatch.add_argument("--tests", default="", help="the test template that says how the worker tests when the setting is Run the tests it wrote: Scoped tests by default, Full suite, or one of the project's own; with Hand the tests over the worker runs none, and with Test budget it tests only through journal tests turn")
        dispatch.add_argument("--profile", required=True, help="the worker profile it works by: senior, on Opus, for a job that needs judgement; medior, on Sonnet, for one whose shape is settled")
        dispatch.add_argument("--model", help="a model other than the profile's")
        dispatch.add_argument("--worktree", action="store_true", help="in a worktree of its own, for code; then name its library folders with --libraries or --copies, or say --no-libraries")
        dispatch.add_argument("--libraries", default="", help="library folders the worktree links to the main checkout's, comma separated, such as node_modules,.venv")
        dispatch.add_argument("--copies", default="", help="library folders the worktree gets copies of its own of, comma separated, such as vendor for composer, whose autoloader would load the main checkout's classes through a link")
        dispatch.add_argument("--no-libraries", action="store_true", help="a worktree with no library folders, for a job that changes the libraries themselves")
        dispatch.add_argument("--pool", action="store_true", help="to the team's pool: a teammate's machine with a free worker slot runs it in a worktree cut from your environment's head, which is pushed to origin first; with --worktree, a profile the team allows its pool, and no --model")
        dispatch.add_argument("--needs-secrets", action="store_true", help="the job uses secrets kept on this machine, so it cannot go to the pool")
        dispatch.add_argument("--fresh", action="store_true", help="a fresh worker even though one back already worked on the same files")
        dispatch.add_argument("--report", nargs="+", help="when it reports on a queue: queue (once its queue is empty, the default), each (after every task) or every <n> (after every n tasks)")
        dispatch.add_argument("--task", type=int, required=True, help="the task it works on: an open one with a brief, or the one you hold; it is the worker's alone until merged or released")
        release = self.verb(verbs, "release", "let a worker go whose run ended without clocking out, which frees its task")
        release.add_argument("n", type=int)
        release.add_argument("--drop", action="store_true", help="also open again the tasks of its queue it finished and that wait for the merge; their commits stay on its branch")
        self.verb(verbs, "merge", "take in a clocked-out worker's checked work, which closes its task").add_argument("n", type=int)
        check = self.verb(verbs, "check", "check one proof of a clocked-out worker, or send it back short")
        check.add_argument("n", type=int)
        check.add_argument("point", type=int)
        check.add_argument("--short", help="what is missing; the worker is sent it in its last session")
        check.add_argument("--task", type=int, default=0, help="a task of its queue it finished before the one it is on, which waits for the same merge; the one it is on when not named")
        report = self.verb(verbs, "report", "the worker reports back")
        report.add_argument("n", type=int)
        report.add_argument("text")
        line = self.verb(verbs, "send", "give a worker that reported or was stopped its next job, in its last session with its memory of the last")
        line.add_argument("n", type=int)
        line.add_argument("brief")
        line.add_argument("--task", type=int, help="the task this job works on, which its plan then leaves to it")
        line.add_argument("--model", help="the model it runs the job on from now, in the same session and worktree")
        line.add_argument("--profile", help="the worker profile it works by from now, and its model unless --model names one")
        queue = self.verb(verbs, "queue", "hand a worker open tasks to take next, in order, a started or paused one in your own hands let go to it: each is delegated to it at once, and the next is sent to it when its work is merged")
        queue.add_argument("n", type=int)
        queue.add_argument("tasks", type=int, nargs="+")
        queue.add_argument("--report", nargs="+", help="when it reports from now: each, queue or every <n>; unnamed, its choice stays")
        queue.add_argument("--first", action="store_true", help="put the tasks at the head of the queue, in the order given, taking one from another worker's queue if it is there, so the first is the next one sent")
        self.verb(verbs, "drain", "give back every task waiting in a worker's queue, open again, in one mark; the task it works on stays its").add_argument("n", type=int)
        notify = self.verb(verbs, "notify", "give a running worker a message in its live session")
        notify.add_argument("n", type=int)
        notify.add_argument("text")
        wait = self.verb(verbs, "wait", "wait until these workers have reported")
        wait.add_argument("on", type=int, nargs="+")
        wait.add_argument("--output", type=int, action="append", default=[], metavar="N", help="a command's output the same wait also ends on, such as a test run; more than one waits for all")
        for verb, help in (("stop", "end a worker"), ("complete", "a worker's report acted on: merged, used or set aside, so it is no longer named")):
            retire = self.verb(verbs, verb, help)
            retire.add_argument("n", type=int)
            retire.add_argument("--why", default="", help="why the worker cannot be reused for the next job")
        discard = self.verb(verbs, "discard", "retire a worker and throw its unmerged commits away, on purpose")
        discard.add_argument("n", type=int)
        discard.add_argument("--why", required=True, help="why its work is thrown away instead of merged")
        self.verb(verbs, "list", "every worker, and the subagents this agent started")
        self.verb(verbs, "open", "the workers still to act on: out, clocked out with work to check, or ended without clocking out, and the subagents still running")
        self.verb(verbs, "peers", "for a worker: the other workers of the agent that dispatched it, out or idle, and what each is on")

    def provider_default(self, caller: Caller) -> str:
        return self.providers.default().name if caller.provider is None else caller.provider

    def is_test_command_missing(self) -> bool:
        return self.settings.option(WorkersOptions.TESTING) == JOURNAL_TESTING and not str(self.settings.option(WorkersOptions.TEST_COMMAND)).strip()

    @staticmethod
    def testing_title(mode: str, title: str) -> str:
        fixed = {MERGER_TESTING: ZERO_TESTS.title, TEST_BUDGET: BUDGET_TESTS.title, JOURNAL_TESTING: JOURNAL_TESTS.title}
        return fixed.get(mode) or title or SCOPED_TESTS.title

    def testing_template(self, title: str) -> Template:
        mode = self.settings.option(WorkersOptions.TESTING)
        title = self.testing_title(mode, title)
        matches = self.templates.testing_titled(title, "worker")
        if not matches:
            raise Rejection(f"no test template is titled {title}: name one with --tests, {', '.join(template.title for template in self.templates.testing('worker'))}")
        return matches[0]

    def dispatch(self, args: Namespace, caller: Caller) -> int:
        if self.starts.hosted_refusal():
            raise Rejection(self.starts.hosted_refusal())
        if self.is_test_command_missing():
            raise Rejection(TEST_COMMAND_MISSING)
        if args.pool and args.report and ReportChoice.argument(args.report).tasks != 1:
            raise Rejection(POOL_REFUSAL)
        self.worker_profile(args.profile)
        output = self.workers.held_locally()
        maximum = self.settings.integer(WorkersOptions.WORKER_LIMIT)
        if maximum and len(output) >= maximum:
            waiting = self.workers.checkable_workers()
            raise Rejection((WorkersNudges.PLACES_FULL.create(n=min(waiting, key=lambda worker: worker.silence.timeout.start).id) if waiting else WorkersNudges.WORKER_OVERFLOW.create(out=len(output))).rendered())
        if args.pool and self.pool_refusal(args):
            raise Rejection(self.pool_refusal(args))
        task = self.assignment(args.task, caller)
        provider = args.provider or self.provider_default(caller)
        moment = datetime.now(timezone.utc).timestamp()
        if args.changes.strip().lower() in EMPTY_CHANGES:
            raise Rejection("a worker writes: name what it changes with --changes; a job that only reads, searches, researches or reviews goes to a subagent with the Agent tool")
        links, copies = self.library_names(args)
        testing = self.testing_template(args.tests)
        worker = Worker(name=args.name, brief="\n\n".join(part for part in (task.brief, args.brief, f"You change: {args.changes}", f"How you test: {testing.brief}") if part), provider=provider, model=args.model or self.model(args.profile, provider), profile=args.profile, worktree=args.worktree, library_links=links, library_copies=copies, dispatcher=caller.session, report_choice=self.report_choice(args))
        worker = self.workers.save(worker.contacted(moment), caller.actor)
        if args.pool:
            return self.pooled(worker, task, args, caller, moment)
        return self.launched(worker, task, caller)

    # the report choice named, else the queue's end, but after each task for a pool worker, which takes one task per request
    @staticmethod
    def report_choice(args: Namespace) -> ReportChoice:
        if args.report:
            return ReportChoice.argument(args.report)
        return ReportChoice(1) if args.pool else ReportChoice()

    def launched(self, worker: Worker, task: Task, caller: Caller) -> int:
        try:
            repositories = self.runner.workplace(worker)
        except WorktreeFailure as failed:
            self.workers.delete(worker, caller.actor)
            raise Rejection(f"worker {worker.name} was not dispatched: {failed}") from failed
        self.tasks.handover(task, Ref.build(worker), caller.actor)
        self.launch.launched(worker, caller.actor, repositories, self.branch.name(worker) if worker.worktree else "")
        print(f"worker {worker.id} {worker.name} dispatched on {worker.provider} {worker.model}; it reports in the chat when it ends")
        return 0

    def pooled(self, worker: Worker, task: Task, args: Namespace, caller: Caller, moment: float) -> int:
        try:
            request = self.pool.send(worker, task)
        except Rejection:
            self.workers.delete(worker, caller.actor)
            raise
        self.tasks.handover(task, Ref.build(worker), caller.actor)
        self.workers.save(self.workers.find(worker.row_id).with_(pool_request=request, base=WorkerBranch.pool_base(worker), branch=self.branch.name(worker)).dispatched(moment), caller.actor)
        print(f"worker {worker.id} {worker.name} sent to the team's pool as request {request}; a teammate's machine with a free slot takes it up, and it reports in the chat when it ends")
        return 0

    def pool_refusal(self, args: Namespace) -> str:
        allowed = self.settings.texts(WorkersOptions.POOL_PROFILES)
        refusals = (
            (not self.account.is_joined(), "the pool is the team's: this journal has joined no team, so dispatch without --pool"),
            (not args.worktree, "a pool worker works in a worktree cut from your environment's head: add --worktree with its library folders"),
            (bool(args.model), "a pool worker runs the model its profile names on the machine that takes it: leave --model out"),
            (args.profile not in allowed, f"the team's pool runs only the profiles {', '.join(allowed) or 'none'}: name one with --profile, or dispatch without --pool"),
            (args.needs_secrets, "a job that uses this machine's secrets stays on this machine: dispatch it without --pool"),
            (bool(self.branch.inner_folders()), f"the project holds repositories of its own ({', '.join(self.branch.inner_folders())}), which origin does not carry, so its workers cannot go to the pool: dispatch without --pool"),
        )
        return next((line for refused, line in refusals if refused), "")

    def library_names(self, args: Namespace) -> tuple[tuple[str, ...], tuple[str, ...]]:
        links = tuple(name.strip().rstrip("/") for name in args.libraries.split(",") if name.strip())
        copies = tuple(name.strip().rstrip("/") for name in args.copies.split(",") if name.strip())
        if not args.worktree and (links or copies or args.no_libraries):
            raise Rejection("library folders are for a worker with a worktree: add --worktree, or leave them out")
        if args.worktree and not (links or copies or args.no_libraries):
            raise Rejection("a worker with a worktree names its library folders: --libraries node_modules,.venv links the main checkout's, --copies vendor gives it copies of its own (composer's vendor must be copied, since its autoloader loads classes from where vendor really lives), or --no-libraries for none")
        if args.no_libraries and (links or copies):
            raise Rejection("--no-libraries says none, so name no folders beside it")
        refusal = self.libraries.refusal((*links, *copies))
        if refusal:
            raise Rejection(refusal)
        return links, copies

    def assignment(self, n: int, caller: Caller) -> Task:
        task = self.tasks.find(n)
        for plan in self.plans.unapproved(task):
            plan.task_startable(task.id)
        if self.is_holder(task, caller) or task.is_assignable():
            return task
        raise Rejection(ASSIGNMENT_REFUSALS.get(task.state, EMPTY_BRIEF_REFUSAL).format(n=n, state=task.state))

    def is_holder(self, task: Task, caller: Caller) -> bool:
        agents = [] if caller.session is None else self.agents.global_matching(session=caller.session)
        return bool(agents) and self.tasks.holder(task) == Ref.build(agents[0])

    def worker_profile(self, profile: str) -> None:
        if self.profiles.kind(profile) != ProfileKind.WORKER:
            raise Rejection(f"{profile} is no worker profile: name one with --profile, senior for a job that needs judgement or medior for one whose shape is settled; a subagent profile only reads, so send it with the Agent tool")

    def staffing(self, args: Namespace) -> tuple[str, str | None]:
        worker = self.workers.find(args.n)
        if args.profile is None:
            return args.model or worker.model, worker.profile
        self.worker_profile(args.profile)
        return args.model or self.model(args.profile, worker.provider), args.profile

    def model(self, profile: str, provider: str) -> str:
        return self.providers.lookup(provider).profile_model(self.profiles.read(profile))

    def report(self, args: Namespace, caller: Caller) -> int:
        if caller.worker_number is not None and caller.worker_number != args.n:
            raise Rejection(f"worker {args.n} is not you: a worker reports for itself, worker {caller.worker_number}")
        worker = self.workers.find(args.n)
        if caller.worker_number is not None and worker.token_hash:
            raise Rejection("a worker reports by clocking out: journal clock-out \"<report>\", once each point of its brief has a proof")
        message = self.reports.file(worker.with_(session=worker.session if caller.session is None else caller.session, touched_paths=self.branch.touched(worker)), args.text, caller.actor)
        print(f"worker {worker.id} reported in message {message.id}")
        return 0

    def send(self, args: Namespace, caller: Caller) -> int:
        holdings = self.tasks.holder_task_ids(Ref(Worker.table(), args.n))
        if args.task and holdings and args.task not in holdings:
            raise Rejection(f"worker {args.n} holds task {holdings[0]} until its work is merged or released: send it the next job on that task, or release it first")
        if caller.worker_number is not None and (args.model or args.profile):
            raise Rejection("only the agent that dispatched a worker changes its model or its profile")
        worker = self.actions.peer_send(args.n, args.brief, caller.worker_number, caller.actor) if caller.worker_number is not None else self.actions.send_on(args.n, args.brief, *self.staffing(args), caller.session, caller.actor)
        if args.task:
            self.tasks.handover(self.tasks.find(args.task), Ref.build(worker), caller.actor)
        print(f"worker {worker.id} {worker.name} told, on {worker.model}; it reports in the chat when it ends")
        return 0

    def check(self, args: Namespace, caller: Caller) -> int:
        if args.short:
            task = self.actions.short_check(args.n, args.point, args.short, caller.actor, args.task)
            print(f"point {args.point} of task {task.id} sent back short to worker {args.n}")
            return 0
        warning = self.actions.unrun(args.n, args.point, args.task) if self.settings.option(WorkersOptions.TESTING) == MERGER_TESTING else ""
        task = self.actions.check(args.n, args.point, caller.actor, args.task)
        print("\n".join(filter(None, [f"point {args.point} of task {task.id} checked", warning])))
        return 0

    def merge(self, args: Namespace, caller: Caller) -> int:
        outcome = self.actions.merge(args.n, caller.actor, MergeSteps(print))
        print(f"task {outcome.task.id} done: {outcome.task.outcome}")
        print(outcome.worktree or "it had no worktree")
        if outcome.finished:
            print(f"closed with it, from its queue: {', '.join(f'task {task.id}' for task in outcome.finished)}")
        if outcome.next_task:
            print(outcome.next_task)
        if self.settings.option(WorkersOptions.MODE) == WorkersProfiles.ORCHESTRATOR.mode:
            print(f"run the whole suite now: it has not passed since the merges of {self.checks.check().workers_line()}")
        return 0

    def queue(self, args: Namespace, caller: Caller) -> int:
        worker = self.workers.find(args.n)
        if args.report:
            worker = self.actions.chose_report(worker.id, ReportChoice.argument(args.report), caller.actor)
        for n in reversed(args.tasks) if args.first else args.tasks:
            self.tasks.let_go(self.tasks.find(n), self.taking.holder(caller), caller.actor)
            (self.tasks.queued_first if args.first else self.tasks.queued)(self.tasks.find(n), Ref.build(worker), caller.actor)
        print(f"worker {worker.id} {worker.name} queue: {', '.join(f'task {task.id}' for task in self.tasks.queue(Ref.build(worker)))}, each delegated to it; it reports {worker.report_choice.label()}")
        if not worker.is_running() and self.tasks.holder_task(Ref.build(worker)) is None:
            print(self.actions.next_job(worker.id, caller.actor))
        advice = self.fitting.advice(self.workers.find(worker.id), time.time())
        if advice:
            print(advice)
        return 0

    def drain(self, args: Namespace, caller: Caller) -> int:
        worker = self.workers.find(args.n)
        waiting = self.tasks.queue(Ref.build(worker))
        self.tasks.unqueued(Ref.build(worker), caller.actor)
        if waiting:
            self.workers.save(worker.queue_drained([task.id for task in waiting], time.time()), caller.actor)
        print(f"worker {worker.id} {worker.name}: {', '.join(f'task {task.id}' for task in waiting)} given back, open again" if waiting else f"worker {worker.id} {worker.name} had nothing queued")
        return 0

    def release(self, args: Namespace, caller: Caller) -> int:
        worker = self.actions.release_dropping(args.n, caller.actor) if args.drop else self.actions.release(args.n, caller.actor)
        print(f"worker {worker.id} {worker.name} released; its task is free again")
        return 0

    def notify(self, args: Namespace, caller: Caller) -> int:
        worker = self.actions.peer_notify(args.n, args.text, caller.worker_number, caller.actor) if caller.worker_number is not None else self.actions.notify(args.n, args.text, caller.actor)
        print(f"worker {worker.id} {worker.name} has the message in its session")
        return 0

    def wait(self, args: Namespace, caller: Caller) -> int:
        workers = [self.workers.find(n) for n in args.on]
        for worker in workers:
            if not worker.is_pending():
                print(self.state_line(worker))
        crew = [worker for worker in workers if worker.is_pending()]
        runs = self.targets.outputs.unended_outputs(args.output)
        if crew or runs:
            numbers = ", ".join(str(worker.id) for worker in crew)
            focus = f"the work of workers {numbers}" if crew else "the test run"
            refs = [worker.mention().ref() for worker in crew] + [self.targets.ref(run) for run in runs]
            self.events.wait_declared(focus + "".join(f" and output {run.id}" for run in runs), ",".join(refs), caller)
            print(f"awaiting {', '.join([f'workers {numbers}'] * bool(crew) + [f'output {run.id}' for run in runs])}: you are told as each ends, and when the last is done")
        return 0

    def state_line(self, worker: Worker) -> str:
        if worker.state != WorkerState.DELIVERED:
            return f"worker {worker.id}, {worker.name}, is not out: it is {worker.state}"
        task_ids = self.tasks.holder_task_ids(Ref.build(worker))
        if not task_ids:
            return f"worker {worker.id}, {worker.name}, clocked out and holds no task"
        return f"worker {worker.id}, {worker.name}, already clocked out: task {task_ids[0]} is ready to check; read its proofs with journal task show {task_ids[0]}, then journal worker check {worker.id} <point>"

    def stop(self, args: Namespace, caller: Caller) -> int:
        self.actions.stop(args.n, args.why, caller.actor)
        print(f"worker {args.n} stopped" + (f": {args.why}" if args.why else ""))
        return 0

    def complete(self, args: Namespace, caller: Caller) -> int:
        worker, dropped = self.actions.complete(args.n, args.why, caller.actor)
        print(f"worker {worker.id}'s report is acted on" + (f": {args.why}" if args.why else "") + (f"; {dropped}" if dropped else ""))
        return 0

    def discard(self, args: Namespace, caller: Caller) -> int:
        worker, dropped = self.actions.discard(args.n, args.why, caller.actor)
        print(f"worker {worker.id} is retired and its work thrown away: {args.why}" + (f"; {dropped}" if dropped else ""))
        return 0

    def peers(self, args: Namespace, caller: Caller) -> int:
        if caller.worker_number is None:
            raise Rejection("only a worker has peers: `journal worker list` lists the workers you dispatched")
        sender = self.workers.find(caller.worker_number)
        peers = self.workers.peers(sender)
        for worker in peers:
            print(f"{worker.id:>4}  {'out' if worker.is_running() else 'idle':<5} {worker.name}: {worker.brief}")
        print(f"`journal worker notify <n> \"<text>\"` tells one that is out, `journal worker send <n> \"<job>\"` gives one that is idle a job" if peers else "no other worker of the agent that dispatched you is out or idle")
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        workers = self.workers.scoped()
        for worker in workers:
            print(f"{worker.id:>4}  {worker.state:<10} {worker.name}: {CardDetail.shortened(worker.brief)}")
            print(self.standing_line(worker))
            if not worker.is_running():
                print(f"{'':>16}files: {worker.files_line()}")
        output = [str(worker.id) for worker in workers if worker.is_running()]
        if output:
            print(f"`journal worker wait {' '.join(output)}` waits for a report; listing again does not bring it sooner")
        self.print_subagents(caller.session)
        return 0

    def open(self, args: Namespace, caller: Caller) -> int:
        workers = self.workers.open_workers()
        for worker in workers:
            print(f"{worker.id:>4}  {worker.state:<10} {worker.name}: {CardDetail.shortened(worker.brief)}")
            print(self.standing_line(worker))
        subagents = [] if caller.session is None else self.subagents.running_session_subagents(caller.session)
        for subagent in subagents:
            print(f"{subagent.id:>4}  {subagent.state:<10} {subagent.agent_type}: {subagent.task}")
        if not workers and not subagents:
            print("no worker or subagent to act on")
        return 0

    @staticmethod
    def standing_line(worker: Worker) -> str:
        return f"{'':>16}on {worker.model}, ${worker.cost_dollars:.2f} spent, sent back {worker.rejections()} times on this task, reports {worker.report_choice.label()}"

    def print_subagents(self, session: str | None) -> None:
        subagents = [] if session is None else self.subagents.session_subagents(session)
        if subagents:
            print("subagents this agent started:")
        for subagent in subagents:
            print(f"{subagent.id:>4}  {subagent.state:<10} {subagent.agent_type}: {subagent.task}")
            if subagent.is_idle():
                print(f"{'':>16}session: {subagent.session}")
        if any(subagent.is_idle() for subagent in subagents):
            print("an idle subagent takes its next job by SendMessage to its session; `journal subagent retire <n>` lets one go")
