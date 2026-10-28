from argparse import Namespace
from dataclasses import replace

from journal.console.support.hub_choice import HubChoice
from journal.console.support.hub_rows import HubRows
from journal.support.row_labels import RowLabels
from journal.console.command import Command
from journal.support.caller import Caller
from journal.features.plans.support.plan_testing import PlanTesting
from journal.features.plans.support.review_rounds import ReviewRounds
from journal.features.tasks.active_task import ActiveTask
from journal.features.tasks.support.waits import Waits
from journal.features.workers.support.subagent_entries import SubagentEntries
from journal.models.link import Link
from journal.models.phase import Phase
from journal.features.plans.support.phase_testing import PhaseTesting
from journal.features.plans.support.plan_statuses import PlanStatuses
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.links import Links
from journal.support.rejection import Rejection
from journal.repositories.phases import Phases
from journal.repositories.plans import PHASE_LINK, PLAN_LINK, PHASE_TASK_LINK, Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.sync.hub_drives import HubDrives
from journal.support.row_destination import RowDestination
from journal.features.workers.support.plan_approval import PlanApproval
from journal.features.workers.workers_options import WorkersOptions
from journal.features.workers.support.work_mode import WorkMode
from journal.support.time_source import TimeSource
CURRENT = "current"


APPROVAL_REFUSAL = "only the user approves this plan: ask, then wait for their word"

class PlanCommand(Command):
    noun = "plan"
    uncut_verbs = frozenset({"start", "show", "priorities"})

    def __init__(self, plans: Plans, phases: Phases, tasks: Tasks, links: Links, subagents: SubagentEntries, waits: Waits, rounds: ReviewRounds, taking: ActiveTask, testing: PlanTesting, hub_rows: HubRows, hub: HubChoice, labels: RowLabels, settings: SettingRows, drives: HubDrives, statuses: PlanStatuses, phase_testing: PhaseTesting, destination: RowDestination, orchestrator: WorkMode, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.orchestrator = orchestrator
        self.plans, self.phases, self.tasks, self.links, self.subagents, self.waits = plans, phases, tasks, links, subagents, waits
        self.rounds, self.taking, self.plan_testing, self.hub_rows, self.hub, self.labels = rounds, taking, testing, hub_rows, hub, labels
        self.settings, self.drives, self.statuses, self.phase_testing, self.destination = settings, drives, statuses, phase_testing, destination

    def arguments(self, verbs) -> None:
        creation = self.verb(verbs, "create", "draft a plan")
        creation.add_argument("title")
        creation.add_argument("--brief", default="")
        creation.add_argument("--team", default="", help="make it in the hub of the joined team of this name")
        addition = self.verb(verbs, "add", "add a task to a plan, after the ones it has")
        addition.add_argument("n", type=int)
        addition.add_argument("title")
        addition.add_argument("--brief", default="")
        addition.add_argument("--first", action="store_true", help="put it before the tasks the plan has")
        brief = self.verb(verbs, "brief", "set a plan's goal, what is true when it is done")
        brief.add_argument("n", type=int)
        brief.add_argument("text")
        rephase = self.verb(verbs, "rephase", "a phase's title or its complete-when line written anew")
        rephase.add_argument("n", type=int)
        rephase.add_argument("phase", type=int, help="the phase's number from 1")
        rephase.add_argument("--title", default="")
        rephase.add_argument("--when", default="")
        phase = self.verb(verbs, "phase", "add a phase to a plan, after the ones it has")
        phase.add_argument("n", type=int)
        phase.add_argument("title")
        phase.add_argument("--when", default="", help="what is true when the phase is complete")
        phase.add_argument("--checkpoint", action="store_true", help="the user looks before the plan goes on")
        todos = self.verb(verbs, "todos", "put tasks under a phase of a plan, by the phase's number from 1")
        todos.add_argument("n", type=int)
        todos.add_argument("phase", type=int)
        todos.add_argument("tasks", type=int, nargs="+")
        removal = self.verb(verbs, "remove", "take tasks out of a plan and its phases; they stay open as tasks of their own")
        removal.add_argument("n", type=int)
        removal.add_argument("tasks", type=int, nargs="+")
        ready = self.verb(verbs, "ready", "the plan is built: every phase has its tasks, and the user may approve it")
        ready.add_argument("n", type=int)
        ready.add_argument("--changed", help="after a review: what the round changed in the plan, in one line (tasks added, merged, moved, reworded)")
        self.verb(verbs, "review", "reviewers are reading the plan: it cannot be approved until they are back and their findings are in it").add_argument("n", type=int)
        self.verb(verbs, "approve", "the user's word: the plan may start").add_argument("n", type=int)
        self.verb(verbs, "start", "follow an approved plan, or go on past a checkpoint: its next open task is started").add_argument("n", type=int)
        self.verb(verbs, "pause", "put a plan aside").add_argument("n", type=int)
        self.verb(verbs, "card", "show a plan the user dismissed on the plan card above the chat again").add_argument("n", type=int)
        block = self.verb(verbs, "block", "a started plan waits on one thing before any of its work can go on; a plan whose every task left is blocked blocks itself")
        block.add_argument("n", type=int)
        block.add_argument("why", nargs="?", default="")
        Waits.arguments(block, "plan")
        self.verb(verbs, "unblock", "what the plan waited on came: it is started again").add_argument("n", type=int)
        self.verb(verbs, "cancel", "a plan given up, with the tasks that are its alone; one another live plan holds stays").add_argument("n", type=int)
        driving = self.verb(verbs, "drive", "follow a hub plan from this environment: it and its tasks read as this environment's, and no other environment or machine drives it until you release it")
        driving.add_argument("n", type=int)
        driving.add_argument("--take-over", action="store_true", help="take it from whoever drove it last, once their lease has lapsed, 15 minutes after its last renewal")
        self.verb(verbs, "release", "let a hub plan you drive go, so anyone may drive it").add_argument("n", type=int)
        self.verb(verbs, "show", "a plan and its tasks").add_argument("n", help="the plan's number, a team's name and number such as acme:12, or current for every started plan")
        self.verb(verbs, "list", "every plan here")
        priorities = self.verb(verbs, "priorities", "the order the started plan's open work goes in, and why: what unblocks the most others or you first")
        priorities.add_argument("order")
        priorities.add_argument("--plan", type=int, help="the plan, when it is not the started one")
        testing = self.verb(verbs, "testing", "how the plan's agent is told to test, by a plan testing template's title, or none")
        testing.add_argument("n", type=int)
        testing.add_argument("title")

    def create(self, args: Namespace, caller: Caller) -> int:
        if self.is_orchestrator(caller) and not self.settings.option(WorkersOptions.ORCHESTRATOR_WRITES_PLANS):
            raise Rejection("the user writes the plans here: Orchestrator may write plans is off, so ask them for one")
        with self.hub.writing_in(args.team):
            plan = self.plans.save(Plan(title=args.title, brief=args.brief), caller.actor)
        print(f"{self.labels.name('plan', plan)} {plan.state}")
        return 0

    def add(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.n)
        previous = self.plans.plan_tasks(plan) if args.first else []
        task = self.tasks.save(Task(environment_id=plan.environment_id, title=args.title, brief=args.brief), caller.actor)
        self.links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), caller.actor)
        for counterpart in previous:
            self.relink(counterpart, plan, caller)
        print(f"{self.labels.name('task', task)} added to {self.labels.name('plan', plan)}{' first' if args.first else ''}{self.destination.phrase(task)}")
        return 0

    def relink(self, task: Task, plan: Plan, caller: Caller) -> None:
        for link in self.links.connecting(task, plan):
            self.links.delete(link, caller.actor)
        self.links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), caller.actor)

    def rephase(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.n)
        phase = self.plans.plan_phases(plan)[args.phase - 1]
        changed = phase.with_(title=args.title or phase.title, completion_rule=args.when or phase.completion_rule)
        self.phases.save(changed, caller.actor)
        print(f"phase {args.phase} of plan {plan.id} is now: {changed.title}")
        return 0

    def phase(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.n)
        phase = self.phases.save(Phase(environment_id=plan.environment_id, title=args.title, completion_rule=args.when, checkpoint=args.checkpoint), caller.actor)
        self.links.save(Link(source=Ref.build(phase), target=Ref.build(plan), link_type=PHASE_TASK_LINK), caller.actor)
        print(f"phase {len(self.plans.plan_phases(plan))} of plan {plan.id}")
        return 0

    def todos(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.n)
        phases = self.plans.plan_phases(plan)
        if not 1 <= args.phase <= len(phases):
            raise Rejection(f"plan {plan.id} has {len(phases)} phases: name one by its number from 1")
        phase = phases[args.phase - 1]
        for n in args.tasks:
            task = self.tasks.find(n)
            if not self.links.connecting(task, plan):
                self.links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), caller.actor)
            for link in [link for counterpart in phases for link in self.links.connecting(task, counterpart)]:
                self.links.delete(link, caller.actor)
            self.links.save(Link(source=Ref.build(task), target=Ref.build(phase), link_type=PHASE_LINK), caller.actor)
        print(f"tasks {', '.join(str(n) for n in args.tasks)} under phase {args.phase} of plan {plan.id}")
        return 0

    def remove(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.n)
        for n in args.tasks:
            self.plans.remove_task(plan, self.tasks.find(n), caller.actor)
        print(f"tasks {', '.join(str(n) for n in args.tasks)} taken out of plan {plan.id}")
        return 0

    def ready(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.n)
        phases = self.plans.plan_phases(plan)
        if not phases:
            raise Rejection(f"plan {plan.id} has no phase yet: journal plan phase {plan.id} \"<title>\" --when \"<complete when>\"")
        empty = [i for i, phase in enumerate(phases, 1) if not self.plans.phase_tasks(phase)]
        if empty:
            raise Rejection(f"phase {', '.join(str(i) for i in empty)} of plan {plan.id} has no task yet: journal plan todos {plan.id} <phase> <tasks>")
        output = self.subagents.running_mentioning(caller.session, f"plan {plan.id}") if plan.is_reviewing() and caller.session is not None else 0
        if output:
            raise Rejection(f"plan {plan.id} is in review, {output} reviewers still out: wait, add what they found, then ready it")
        if plan.is_reviewing():
            self.close_round(plan, args.changed, caller)
        plan = self.plans.save(plan.ready(self.time_source.seconds()), caller.actor)
        print(f"plan {plan.id} ready: the user approves it on the plan page")
        return 0

    def close_round(self, plan: Plan, changed: str | None, caller: Caller) -> None:
        if changed is None:
            raise Rejection(f"plan {plan.id} is in review: `journal plan ready {plan.id} --changed \"<what this round changed>\"`")
        self.rounds.close(plan, changed, caller)

    def review(self, args: Namespace, caller: Caller) -> int:
        self.rounds.begin(self.plans.find(args.n), caller.actor)
        print(f"plan {args.n} in review: put what the reviewers find straight into it, then journal plan ready {args.n}")
        return 0

    def approve(self, args: Namespace, caller: Caller) -> int:
        if not caller.actor.is_user() and not self.is_approving_orchestrator(caller):
            raise Rejection(APPROVAL_REFUSAL)
        plan = self.plans.find(args.n)
        if not caller.actor.is_user() and not PlanApproval(self.settings.option(WorkersOptions.ORCHESTRATOR_PLAN_APPROVAL)).allows(plan, caller.actor):
            raise Rejection(APPROVAL_REFUSAL)
        plan = self.plans.approve(plan, caller.actor)
        print(f"plan {plan.id} {plan.state}")
        return 0

    def is_approving_orchestrator(self, caller: Caller) -> bool:
        return self.is_orchestrator(caller) and bool(self.settings.option(WorkersOptions.ORCHESTRATOR_APPROVES_PLANS))

    def is_orchestrator(self, caller: Caller) -> bool:
        return caller.is_main_agent() and self.orchestrator.delegates_work()

    def start(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.n)
        if refusal := self.phase_testing.refusal(plan):
            raise Rejection(refusal)
        plan = self.plans.opened(plan, caller.actor) if self.orchestrator.delegates_work() else self.plans.start(plan, self.taking.holder(caller), caller.actor)
        current = self.plans.started_task(plan)
        print(f"plan {plan.id} {plan.state}" + (f": task {current.id}, {current.title} is started" if current else ""))
        return 0

    def block(self, args: Namespace, caller: Caller) -> int:
        self.waits.refuse_unnamed(args.why, args.on, args.until)
        plan = self.plans.save(self.plans.find(args.n).blocked(args.why, self.time_source.moment().timestamp()), caller.actor)
        self.waits.linked(plan, args.on, args.until, args.every, caller.actor)
        print(f"plan {plan.id} blocked, waiting on: {self.tasks.reason(plan)}")
        return 0

    def unblock(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.save(self.plans.find(args.n).unblocked("the user opened it", self.time_source.moment().timestamp()), caller.actor)
        print(f"plan {plan.id} open again: `journal plan start {plan.id}` goes on with it")
        return 0

    def drive(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.n)
        print(self.drives.drive_line(self.drives.takeover(plan, caller.actor) if args.take_over else self.drives.drive(plan, caller.actor)))
        return 0

    def release(self, args: Namespace, caller: Caller) -> int:
        print(self.drives.release_line(self.drives.release(self.plans.find(args.n), caller.actor)))
        return 0

    def pause(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.postpone(self.plans.find(args.n), caller.actor)
        print(f"plan {plan.id} paused")
        return 0

    def card(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.save(self.plans.find(args.n).card_restored(), caller.actor)
        print(f"plan {plan.id} is shown on the plan card again")
        return 0

    def cancel(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.n)
        cancelled = self.plans.cancel(plan, caller.actor)
        print(f"plan {plan.id} cancelled" + (f", with tasks {', '.join(str(t.id) for t in cancelled)}" if cancelled else ""))
        return 0

    def testing(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.n)
        followed = self.plan_testing.follow(plan, args.title, caller.actor)
        print(f"plan {plan.id} tests this way: {followed[0].brief}" if followed else f"plan {plan.id} follows no testing template")
        return 0

    def priorities(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.find(args.plan) if args.plan else next(iter(self.plans.running_plans()), None)
        if plan is None:
            raise Rejection("no plan is started: name the plan with --plan")
        phases = self.plans.phase_states(plan)
        plan = self.plans.save(plan.prioritised(args.order, plan.current_phase(phases), self.time_source.seconds()), caller.actor)
        print(f"plan {plan.id} priorities recorded")
        return 0

    def brief(self, args: Namespace, caller: Caller) -> int:
        plan = self.plans.save(replace(self.plans.find(args.n), brief=args.text), caller.actor)
        print(f"plan {plan.id} brief set")
        return 0

    def show(self, args: Namespace, caller: Caller) -> int:
        return self.current() if args.n == CURRENT else self.shown(self.plans.find(self.hub_rows.number(args.n)))

    def current(self) -> int:
        started = self.statuses.started()
        if not started:
            print("no plan is started")
        moment = self.time_source.seconds()
        for status in started:
            print(f"started: {status.line(moment)}")
            self.shown(self.plans.find(status.plan_id))
        return 0

    def shown(self, plan: Plan) -> int:
        print(f"plan {plan.id} {plan.state}: {plan.title}")
        if plan.is_started() and (phases := self.plans.phase_states(plan)):
            current = phases[plan.current_phase(phases) - 1]
            print(f"phase in hand: {current.number} of {len(phases)}, {current.phase.title}")
        if plan.priorities:
            print(f"priorities: {plan.priorities}")
        for i, phase in enumerate(self.plans.plan_phases(plan), 1):
            print(f"phase {i}: {phase.title}" + (f" (complete when {phase.completion_rule})" if phase.completion_rule else "") + (" [checkpoint]" if phase.checkpoint else ""))
            for task in self.plans.phase_tasks(phase):
                print(f"{task.id:>4}  {task.state:<8} {task.title}")
        loose = self.plans.loose_tasks(plan)
        if loose:
            print("under no phase yet:")
        for task in loose:
            print(f"{task.id:>4}  {task.state:<8} {task.title}")
        return 0

    def list(self, args: Namespace, caller: Caller) -> int:
        for plan in self.plans.scoped():
            print(f"{plan.id:>4}  {plan.state:<8} {plan.title}")
        return 0
