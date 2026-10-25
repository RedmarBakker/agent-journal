from argparse import Namespace
from dataclasses import replace
from datetime import datetime, timezone

from journal.console.command import HELPER_KINDS, SUBAGENT_KINDS, WORKER_KINDS, Command
from journal.console.support.hub_choice import HubChoice
from journal.features.tasks.support.hub_filing import HubFiling
from journal.support.caller import Caller
from journal.support.row_labels import RowLabels
from journal.support.caller_kind import CallerKind
from journal.engine.clock import Clock
from journal.support.rejection import Rejection
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.active_task import ActiveTask
from journal.features.tasks.support.task_briefing import TaskBriefing
from journal.features.tasks.support.block_check import BlockCheck
from journal.features.tasks.support.message_reminder import MessageReminder
from journal.features.tasks.support.waits import Waits
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.support.task_priority import NORMAL, TaskPriority
from journal.models.task_log import TaskLog
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.support.missing_row import MissingRow
from journal.repositories.task_logs import TaskLogs
from journal.repositories.plans import PHASE_LINK, PLAN_LINK, Plans
from journal.repositories.questions import Questions
from journal.repositories.tasks import Tasks
from journal.features.tasks.support.next_open_task import NextOpenTask
from journal.sync.hub_drives import HubDrives
CURRENT = "current"

# the open tasks a plain task list prints, highest priority first; the rest are counted
LIST_ROWS = 20

class TaskCommand(Command):
    noun = "task"
    callers = {"show": HELPER_KINDS, "list": SUBAGENT_KINDS, "log": WORKER_KINDS}

    def __init__(self, tasks: Tasks, logs: TaskLogs, messages: Messages, links: Links, plans: Plans, taking: ActiveTask, questions: Questions, waits: Waits, briefing: TaskBriefing, clock: Clock, next_task: NextOpenTask, check: BlockCheck, reminder: MessageReminder, labels: RowLabels, hub: HubChoice, filing: HubFiling, drives: HubDrives) -> None:
        self.clock, self.next_task, self.reminder = clock, next_task, reminder
        self.tasks, self.logs, self.messages, self.links, self.plans, self.taking, self.questions, self.waits, self.briefing = tasks, logs, messages, links, plans, taking, questions, waits, briefing
        self.check, self.labels, self.hub, self.filing, self.drives = check, labels, hub, filing, drives

    def arguments(self, verbs) -> None:
        creation = self.verb(verbs, "create", "file a task")
        creation.add_argument("title")
        rename = self.verb(verbs, "rename", "a task's title said again, when the first one was wrong")
        rename.add_argument("n", type=int)
        rename.add_argument("title")
        edit = self.verb(verbs, "edit", "a task's title or brief written anew, as when the user corrects what it is about")
        edit.add_argument("n", type=int)
        edit.add_argument("--title", default="")
        edit.add_argument("--brief", default="", help="the whole brief, which replaces the old one")
        edit.add_argument("--priority", default="", help="low, normal, high, critical or a number")
        edit.add_argument("--from", dest="message", type=int, default=0, help="the user's message this edit comes from")
        brief = self.verb(verbs, "brief", "a task's brief written anew, when what done looks like has changed")
        brief.add_argument("n", type=int)
        brief.add_argument("brief")
        creation.add_argument("--brief", default="")
        creation.add_argument("--team", default="", help="make it in the hub of the joined team of this name, which a journal of one team need not name")
        creation.add_argument("--to", default="", help="file it in the hub as a request for this person")
        creation.add_argument("--to-team", action="store_true", help="file it in the hub as a request for the whole team")
        creation.add_argument("--issue", action="store_true", help="file it in the hub as an issue on the board")
        creation.add_argument("--priority", default="normal", help="low, normal, high, critical or a number")
        creation.add_argument("--start", action="store_true", help="start it at once")
        creation.add_argument("--from", dest="message", type=int, default=0, help="the user's message it was filed from")
        self.verb(verbs, "start", "take a task in hand").add_argument("n", type=int)
        log = self.verb(verbs, "log", "note where a task stands")
        log.add_argument("n", type=int)
        log.add_argument("line")
        finished = self.verb(verbs, "complete", "finish a task")
        finished.add_argument("n", type=int)
        finished.add_argument("--how", default="")
        dropped = self.verb(verbs, "cancel", "give a task up, undone, with why")
        dropped.add_argument("n", type=int)
        dropped.add_argument("--why", required=True)
        block = self.verb(verbs, "block", "a task waits on something outside your hands: blocked, with why, it is neither offered nor nudged")
        block.add_argument("n", type=int)
        block.add_argument("why", nargs="?", default="")
        Waits.arguments(block, "task")
        self.verb(verbs, "unblock", "what it waited on came: the task is open again").add_argument("n", type=int)
        pause = self.verb(verbs, "pause", "set a task aside for something else first, by choice; it stays open and stops being nudged")
        pause.add_argument("n", type=int)
        pause.add_argument("why")
        Waits.arguments(pause, "paused task's wait")
        self.verb(verbs, "resume", "pick a paused task up again").add_argument("n", type=int)
        driving = self.verb(verbs, "drive", "work on a hub task from this environment: it reads as this environment's, and no other environment or machine drives it until you release it")
        driving.add_argument("n", type=int)
        driving.add_argument("--take-over", action="store_true", help="take it from whoever drove it last, once their lease has lapsed, 15 minutes after its last renewal")
        self.verb(verbs, "release", "let a hub task you drive go, so anyone may drive it").add_argument("n", type=int)
        self.verb(verbs, "show", "a task whole: its title, state, plan and phase, brief and every log line in order").add_argument("n", help="the task's number, or current for the task in hand")
        self.verb(verbs, "list", "every task here not closed, and how many are done or cancelled").add_argument("--all", action="store_true", help="every task, the closed ones too")

    def create(self, args: Namespace, caller: Caller) -> int:
        person, team = self.filing.person(args), self.filing.team(args)
        with self.hub.writing_in(team):
            task = self.tasks.save(Task(title=args.title, brief=args.brief, priority=TaskPriority.parsed(args.priority)), caller.actor)
            self.filing.link(task, args, person, team, caller.actor)
            self.message_link(args.message, task, caller)
            if args.start:
                task = self.taking.start(task, caller)
            unfiled = "" if args.message else self.reminder.creation_line(task, self.tasks.previous_creation(task))
            line = f"{self.labels.name('task', task)} {task.state}" + (f" (from message {args.message})" if args.message else "")
        print("\n".join(filter(None, [line, unfiled])))
        return 0

    def message_link(self, message: int, task: Task, caller: Caller) -> None:
        if message:
            self.links.save(Link(source=Ref.build(self.messages.find(message)), target=Ref.build(task), kind=Messages.SUBJECT_LINK), caller.actor)

    def start(self, args: Namespace, caller: Caller) -> int:
        return self.claimed_task(args.n, caller, "started")

    def rename(self, args: Namespace, caller: Caller) -> int:
        old_task = self.tasks.find(args.n)
        task = self.tasks.save(old_task.edited(args.title, old_task.brief, self.clock.time()), caller.actor)
        print("\n".join(filter(None, [f"{self.labels.name('task', task)} is now: {task.title}", self.reminder.line(old_task)])))
        return 0

    def brief(self, args: Namespace, caller: Caller) -> int:
        old_task = self.tasks.find(args.n)
        task = self.tasks.save(old_task.edited(old_task.title, args.brief, self.clock.time()), caller.actor)
        print("\n".join(filter(None, [f"{self.labels.name('task', task)} brief written anew", self.reminder.line(old_task)])))
        return 0

    def edit(self, args: Namespace, caller: Caller) -> int:
        if not args.title and not args.brief and not args.priority and args.message:
            return self.message_linked(args, caller)
        if not args.title and not args.brief and not args.priority:
            raise Rejection("name what changes: --title \"<title>\", --brief \"<the whole brief>\", --priority <level>, --from <message>, or several")
        task = self.tasks.find(args.n)
        priority_task = task.with_(priority=TaskPriority.parsed(args.priority)) if args.priority else task
        new_task = self.tasks.save(priority_task.edited(args.title or task.title, args.brief or task.brief, self.clock.time()), caller.actor)
        self.message_link(args.message, new_task, caller)
        summary = f"{self.labels.name('task', task)} edited: {' and '.join(name for name, value in (('title', args.title), ('brief', args.brief), ('priority', args.priority)) if value)} written anew"
        print("\n".join(filter(None, [summary + (f" (from message {args.message})" if args.message else ""), ("" if args.message else self.reminder.line(task))])))
        return 0

    def message_linked(self, args: Namespace, caller: Caller) -> int:
        task = self.tasks.find(args.n)
        self.message_link(args.message, task, caller)
        print(f"message {args.message} linked to task {task.id}")
        return 0

    def log(self, args: Namespace, caller: Caller) -> int:
        task = self.readable(args.n, caller)
        if caller.kind == CallerKind.MAIN_AGENT and not task.is_started():
            raise Rejection(f"{self.labels.name('task', task)} is not in hand, and a log line is read only while a task runs. Put what it has to know in its brief: read it with journal task show {task.id}, then journal task edit {task.id} --brief \"<the whole brief>\"")
        self.logs.save(TaskLog.build(task, args.line, self.clock.time()), caller.actor)
        print(f"{self.labels.name('task', task)} logged")
        return 0

    def pause(self, args: Namespace, caller: Caller) -> int:
        task = self.tasks.save(self.tasks.find(args.n).paused(args.why, self._time()), caller.actor)
        self.waits.linked(task, args.on, args.until, args.every, caller.actor)
        waits = f", waiting on: {self.tasks.reason(task)}; you are told when that is over" if args.on or args.until else ""
        print(f"{self.labels.name('task', task)} paused{waits}")
        return 0

    def resume(self, args: Namespace, caller: Caller) -> int:
        return self.claimed_task(args.n, caller, "resumed")

    def claimed_task(self, n: int, caller: Caller, manner: str) -> int:
        task = self.taking.start(self.tasks.find(n), caller)
        print("\n".join([f"{self.labels.name('task', task)} {manner}", *self.briefing.lines(task)]))
        return 0

    def drive(self, args: Namespace, caller: Caller) -> int:
        task = self.tasks.find(args.n)
        print(self.drives.drive_line(self.drives.takeover(task, caller.actor) if args.take_over else self.drives.drive(task, caller.actor)))
        return 0

    def release(self, args: Namespace, caller: Caller) -> int:
        print(self.drives.release_line(self.drives.release(self.tasks.find(args.n), caller.actor)))
        return 0

    def block(self, args: Namespace, caller: Caller) -> int:
        self.waits.refuse_unnamed(args.why, args.on, args.until)
        self.check.refuse(args.n, args.on)
        task = self.tasks.save(self.tasks.find(args.n).blocked(args.why, self._time()), caller.actor)
        self.waits.linked(task, args.on, args.until, args.every, caller.actor)
        print(f"{self.labels.name('task', task)} blocked, waiting on: {self.tasks.reason(task)}")
        return 0

    def unblock(self, args: Namespace, caller: Caller) -> int:
        task = self.tasks.save(self.tasks.find(args.n).unblocked("it was unblocked by hand", self._time().timestamp()), caller.actor)
        print(f"{self.labels.name('task', task)} open again")
        return 0

    def complete(self, args: Namespace, caller: Caller) -> int:
        holdings = self.tasks.task_worker_holdings({args.n})
        if args.n in holdings and not caller.actor.is_user():
            raise Rejection(f"task {args.n} is worker {holdings[args.n]}'s: take its work in with journal worker merge {holdings[args.n]} once its proofs are checked")
        task = self.tasks.save(self.tasks.find(args.n).finished(self._time(), args.how), caller.actor)
        print(f"{self.labels.name('task', task)} done")
        self._name_next(task)
        return 0

    def cancel(self, args: Namespace, caller: Caller) -> int:
        task = self.tasks.save(self.tasks.find(args.n).cancelled(self._time(), args.why), caller.actor)
        print(f"{self.labels.name('task', task)} cancelled")
        self._name_next(task)
        return 0

    def readable(self, n: int, caller: Caller) -> Task:
        return self.tasks.find(n) if caller.worker_number is None else self.tasks.worker_task(n, caller.worker_number)

    def show(self, args: Namespace, caller: Caller) -> int:
        if args.n == CURRENT:
            holder = self.taking.holder(caller)
            current_task = self.tasks.holder_task(holder) if holder is not None else None
            if current_task is None:
                print("no task is in hand")
                return 0
            args.n = current_task.id
        task = self.readable(int(args.n), caller)
        print(f"""{self.labels.name('task', task)}: {task.title}
state: {task.state}
{self.place(task)}
{self.briefing.whole(task)}""")
        return 0

    def place(self, task: Task) -> str:
        plan = next((self.plans.find(ref.id) for ref in self.links.targets(task, PLAN_LINK)), None)
        if plan is None:
            return "plan: none"
        phases = self.plans.phase_states(plan)
        held = {ref.id for ref in self.links.targets(task, PHASE_LINK)}
        phase = next((p for p in phases if p.phase.id in held), None)
        return f"plan {plan.id}: {plan.title}" + (f", phase {phase.number} of {len(phases)}: {phase.phase.title}" if phase else "")

    def list(self, args: Namespace, caller: Caller) -> int:
        if args.all:
            print(self.task_lines(self.tasks.scoped()))
            return 0
        print(self.task_lines(self.tasks.unclosed_page(LIST_ROWS)))
        unshown, closed = self.tasks.unclosed_count() - LIST_ROWS, self.tasks.closed_count()
        if unshown > 0:
            print(f"and {unshown} more open: journal task list --all")
        if closed:
            print(f"and {closed} done or cancelled: journal task list --all")
        return 0

    @staticmethod
    def task_lines(tasks: list[Task]) -> str:
        return "\n".join(f"{task.id:>4}  {task.state:<8} {task.title}" + ("" if task.priority == NORMAL else f"  [{TaskPriority.label(task.priority)}]") for task in tasks)

    def _name_next(self, closed: Task) -> None:
        next_open = self.next_task.following(closed)
        if next_open:
            print(next_open.line())

    @staticmethod
    def _time() -> datetime:
        return datetime.now(timezone.utc)
