import time
from pathlib import Path

from journal.events.feature_data import FeatureData
from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.support.timeout import Timeout
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.ticked import Ticked
from journal.events.agent.turn_displayed import TurnDisplayed
from journal.features.workers.support.written_wait import WrittenWait
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.proof_short import ProofShort
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.events.rows.worker_keeps_clashing import WorkerKeepsClashing
from journal.events.rows.worker_limited import WorkerLimited
from journal.events.rows.worker_unfinished import WorkerUnfinished
from journal.events.rows.worker_reported import WorkerReported
from journal.events.rows.places_scaled import PlacesScaled
from journal.events.rows.waits_missing import WaitsMissing
from journal.events.rows.worker_model_mismatch import WorkerModelMismatch
from journal.events.rows.worker_spent import WorkerSpent
from journal.events.rows.task_delegated import TaskDelegated
from journal.models.support.model_fit import OVERPOWERED
from journal.events.rows.worker_stopped import WorkerStopped
from journal.events.rows.worker_test_failed import WorkerTestFailed
from journal.events.rows.worker_queue_empty import WorkerQueueEmpty
from journal.events.rows.worker_mention import WorkerMention
from journal.events.rows.worker_dispatched import WorkerDispatched
from journal.features.workers.support.worker_line import WorkerLine
from journal.features.workers.support.path_mentions import PathMentions
from journal.features.workers.support.release_lines import ReleaseLines
from journal.models.command_output import CommandOutput
from journal.models.subagent import Subagent
from journal.models.support.path_overlap import PathOverlap
from journal.models.worker import Worker
from journal.features.workers.support.workers_data import WorkersData
from journal.support.subagent_dispatch import SubagentDispatch
from journal.features.plans.plans_part import PlansPart
from journal.features.plans.support.plan_status import PlanStatus
from journal.features.tasks.tasks_part import TasksPart
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.support.measure_lines import MeasureLines
from journal.features.workers.fitness_options import FitnessOptions
from journal.features.workers.workers_options import TEST_BUDGET, WorkersOptions
from journal.features.workers.workers_part import WorkersPart
from journal.features.tasks.states.external_wait import ExternalWait

INDEPENDENT_ROLES = ("auditor", "reviewer", "plan-reviewer", "critic")
# the most of a worker's name a failed test run's line carries, so the line stays under 120 characters
TEST_LINE_NAME = 60
# the waiting items a load line names before it counts the rest
# what a line says of a worker whose run hit the time limit
RUN_LIMIT_CAUSE = ": run limit"
# the most of an earlier reason a send-back line quotes
REJECTION_REASON_CHARACTERS = 30
# the send-back on one task at which the orchestrator is told, once, to change the target, the worker or the model
STRUGGLE_REJECTIONS = 3


class WorkersConduct(Conduct):
    """The workers feature's conduct in every state: a subagent past the most allowed at once is blocked, a write into a worker's worktree is blocked, a new subagent whose job names files an idle one of the same kind worked on is blocked in favour of those, unless they are retired, a dispatch whose brief names files an idle worker touched is blocked in favour of that worker, a dispatch past its profile's stored workers is blocked while one of them is idle, retiring an idle worker is blocked until the repeat says why it cannot be reused, the reports not acted on are named at a stop and on the tick, work waiting to be checked is named again every so many tool uses, a worker of this agent's silent for twenty minutes is named once on the tick, a worker this agent dispatches pushes Awaiting on its work, a worker's report is informed as it comes, a worker that stopped at the usage limit is named with the time it goes on by itself, and in orchestrator mode a stop is refused while work this agent sent out waits clocked out, naming each worker, but for one it awaits, the worker itself or a run in its worktree, and once, with journal worker wait, while its workers are only still out; a stop carries the status of every started plan, and names once a started plan that has not moved for the set minutes while another moves, and once a run of the whole suite that failed after merges, with the workers merged since it last passed and the send-back; and, with the test budget, the agent that sent a worker hears in one short line of each of its test runs that failed, unless that line is off, and once when it has failed the set runs in a row, never of a passed run; and in orchestrator mode its load is named in one line from the warning level on, with what waits and the oldest to clear first, the ways to ease it added from the critical level on, and each place the load opens or closes in one line; with the fitness warnings on, each failing measure's one line, as often as its nudge repeats; and in orchestrator mode a merged worker's model that did not fit its work, too strong or too weak, is named in one short line."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        checks = (subagent_reuse_check, limit_check, release_check, worktrees_check, files_check, idle_cap_check, retire_check, open_work_check, measure_check, capability_check, text_wait_check)
        return Transition.merged(self, [check(self, event, settings) for check in checks])

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return Transition.merged(self, [crew_stop(self, event, settings), self.none(*stop_lines(event, settings))])

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        workers = event.data.part(WorkersPart)
        silent = [silence_line(w, workers.last_calls.get(w.id, ""), event.time) for w in workers.dispatched_workers if w.dispatcher == event.session and w.is_silent(event.time)]
        return self.none(*report_mentions(event.data), *silent, *priorities_lines(event, settings), *unmoved_task_lines(event, settings), *unordered_lines(event, settings))

    def on_turn_displayed(self, event: TurnDisplayed, settings: Settings) -> Transition:
        return self.none(*text_wait_lines(event.content, settings)) if event.final else self.none()

    def on_task_delegated(self, event: TaskDelegated, settings: Settings) -> Transition:
        if settings.value(WorkersOptions.MODE) != "orchestrator" or not event.is_unblocking():
            return self.none()
        queues = event.data.part(WorkersPart).queues
        queue_places = [(worker, queue.index(event.task_id) + 1) for worker, queue in queues.items() if event.task_id in queue[1:]]
        return self.none(*(WorkersNudges.UNBLOCKER_QUEUED.create(task=event.task_id, n=worker, place=place) for worker, place in queue_places))

    def on_worker_dispatched(self, event: WorkerDispatched, settings: Settings) -> Transition:
        return self.push(ExternalWait.opened(*event.wait_terms())) if event.awaiter == event.session else self.none()

    def on_worker_limited(self, event: WorkerLimited, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(WorkersNudges.WORKER_LIMITED.create(n=event.worker.id, at=time.strftime("%H:%M", time.localtime(event.resumes_at))))

    def on_worker_unfinished(self, event: WorkerUnfinished, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        if event.times < 2 and event.worker.id in event.data.part(WorkersPart).resumable:
            return self.none()
        return self.none(WorkersNudges.RUN_UNFINISHED.create(n=event.worker.id, cause=RUN_LIMIT_CAUSE if event.is_run_limit else ""))

    def on_worker_delivered(self, event: WorkerDelivered, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        ready = [work for work in event.data.part(WorkersPart).ready_work if work.worker == event.worker.id]
        return self.none(*(WorkersNudges.WORK_READY.create(n=work.worker, name=work.name, task=work.task) for work in ready))

    def on_worker_keeps_clashing(self, event: WorkerKeepsClashing, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(WorkersNudges.BRANCH_KEEPS_CLASHING.create(n=event.worker.id, clashes=event.clashes, clashing=event.clashing))

    def on_worker_reported(self, event: WorkerReported, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(WorkersNudges.WORKER_REPORTED.create(n=event.worker.id, name=event.worker.name))

    def on_worker_test_failed(self, event: WorkerTestFailed, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session) or settings.value(WorkersOptions.TESTING) != TEST_BUDGET:
            return self.none()
        name = event.worker.name[:TEST_LINE_NAME]
        failed = (WorkersNudges.TEST_RUN_FAILED.create(n=event.worker.id, name=name, failed=event.failed),) if settings.value(WorkersOptions.TEST_RUN_LINES) else ()
        failing = (WorkersNudges.WORKER_KEEPS_FAILING.create(n=event.worker.id, name=name, runs=event.runs),) if event.is_streak(settings.integer(WorkersOptions.FAILING_RUNS)) else ()
        return self.none(*failed, *failing)

    def on_worker_spent(self, event: WorkerSpent, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session) or settings.value(WorkersOptions.MODE) != "orchestrator":
            return self.none()
        if not event.is_shaped_work_on_strongest() or not event.crossed(settings.decimal(WorkersOptions.COSTLY_SHAPED_WORK)):
            return self.none()
        return self.none(WorkersNudges.COSTLY_SHAPED_WORK.create(n=event.worker.id, model=event.model, dollars=f"{event.cost_dollars:.2f}"))

    def on_worker_model_mismatch(self, event: WorkerModelMismatch, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session) or settings.value(WorkersOptions.MODE) != "orchestrator":
            return self.none()
        if event.fit == OVERPOWERED:
            return self.none(WorkersNudges.MODEL_OVERPOWERED.create(n=event.worker.id, model=event.model))
        return self.none(WorkersNudges.MODEL_UNDERPOWERED.create(n=event.worker.id, model=event.model, send_backs=event.rejections))

    def on_waits_missing(self, event: WaitsMissing, settings: Settings) -> Transition:
        if event.agent_session != event.session:
            return self.none()
        return self.none(*missing_wait_lines(event))

    def on_places_scaled(self, event: PlacesScaled, settings: Settings) -> Transition:
        if event.agent_session != event.session:
            return self.none()
        nudge = WorkersNudges.PLACE_OPENED if event.opened else WorkersNudges.PLACE_CLOSED
        return self.none(nudge.create(rho=event.rho, minutes=round(event.minutes), places=event.places))

    def on_worker_stopped(self, event: WorkerStopped, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(WorkersNudges.WORKER_STOPPED_UNREPORTED.create(n=event.worker.id, cause=RUN_LIMIT_CAUSE if event.is_run_limit else ""))

    def on_proof_short(self, event: ProofShort, settings: Settings) -> Transition:
        if not event.dispatcher or event.dispatcher != event.session or event.is_reviewers():
            return self.none()
        return self.none(rejection_line(event))

    def on_worker_queue_empty(self, event: WorkerQueueEmpty, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(WorkersNudges.IDLE_WORKER.create(n=event.worker.id))


def missing_wait_lines(event: WaitsMissing) -> list[Nudge]:
    return [WorkersNudges.WAIT_MISSING.create(task=task, other=blocker) for task, blocker in event.waits()]


def rejection_line(event: ProofShort) -> Nudge:
    attempts = len(event.prior_shortfalls) + 1
    if attempts == 1:
        return WorkersNudges.PROOF_REJECTED.create(n=event.worker_id, point=event.point)
    prior_reasons = "; ".join(reason[:REJECTION_REASON_CHARACTERS] for reason in event.prior_shortfalls)
    nudge = WorkersNudges.PROOF_REJECTED_OFTEN if attempts == STRUGGLE_REJECTIONS else WorkersNudges.PROOF_REJECTED_REPEAT
    return nudge.create(n=event.worker_id, point=event.point, times=attempts, earlier=prior_reasons, model=event.model)


def silence_line(worker, last: str, time: float) -> Nudge:
    if worker.silence.is_split_due(time):
        return WorkersNudges.SPLIT_ADVICE.create(n=worker.id, minutes=2 * worker.silence.minutes())
    return WorkersNudges.SILENT_WORKER.create(n=worker.id, minutes=worker.silence.minutes(), last=last)


def stop_lines(event: Stop, settings: Settings) -> tuple[Nudge, ...]:
    return (*report_mentions(event.data), *plan_lines(event.data, event.time, settings), *suite_lines(event.data, settings))


def crew_stop(state: BaseState, event: Stop, settings: Settings) -> Transition:
    if settings.value(WorkersOptions.MODE) != "orchestrator":
        return state.none()
    workers = event.data.part(WorkersPart)
    wait_refs = set(state.targets()) if isinstance(state, ExternalWait) else set()
    delivered = [worker for worker in workers.delivered_workers if not worker.mention().is_other_dispatcher(event.session) and not is_waited(worker, wait_refs, workers.delivered_runs)]
    if delivered:
        return state.refuse(WorkersNudges.DELIVERED_WAITING.create(workers=worker_list(delivered)))
    active_workers = [worker for worker in workers.dispatched_workers if not worker.mention().is_other_dispatcher(event.session) and worker.mention().ref() not in wait_refs]
    if active_workers and not event.prior_refusal:
        return state.refuse(WorkersNudges.ACTIVE_WORKERS.create(workers=worker_list(active_workers), numbers=" ".join(str(worker.id) for worker in active_workers)))
    return state.none()


def is_waited(worker: Worker, waited_refs: set[str], runs: tuple[tuple[int, int], ...]) -> bool:
    return worker.mention().ref() in waited_refs or any(f"{CommandOutput.table()}:{output}" in waited_refs for output, owner in runs if owner == worker.row_id)


def worker_list(workers: list[Worker]) -> str:
    return ", ".join(f"worker {worker.id} ({worker.name})" for worker in workers)


def plan_lines(data: FeatureData, moment: float, settings: Settings) -> tuple[Nudge, ...]:
    if settings.value(WorkersOptions.MODE) != "orchestrator":
        return ()
    started = data.part(PlansPart).started_plans
    if not started:
        return ()
    return (WorkersNudges.STARTED_PLANS.create(plans="; ".join(plan.line(moment) for plan in started)), *stalled_lines(started, moment, settings))


def suite_lines(data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
    if settings.value(WorkersOptions.MODE) != "orchestrator":
        return ()
    check = data.part(WorkersPart).merge_check
    return (WorkersNudges.SUITE_BROKEN.create(run=check.failed_run, workers=check.workers_line(), n=check.merged[-1].id),) if check.failed_run else ()


def stalled_lines(started: tuple[PlanStatus, ...], moment: float, settings: Settings) -> tuple[Nudge, ...]:
    minutes = settings.value(WorkersOptions.PLAN_STALL_MINUTES)
    stalled = [plan for plan in started if minutes and plan.is_stalled(moment, minutes * 60)]
    if len(stalled) == len(started):
        return ()
    return tuple(WorkersNudges.PLAN_STALLED.create(n=plan.plan_id, title=plan.title, since=plan.moved_line(), minutes=minutes) for plan in stalled)


def priorities_lines(event: Ticked, settings: Settings) -> tuple[Nudge, ...]:
    if settings.value(WorkersOptions.MODE) != "orchestrator":
        return ()
    started = event.data.part(PlansPart).started
    if started is None:
        return ()
    interval = settings.integer(WorkersOptions.PRIORITIES_MINUTES) * 60
    if started.priorities_phase == started.current_phase and not (interval and event.time - started.priorities_at >= interval):
        return ()
    return (WorkersNudges.PRIORITIES.create(plan=started.plan_id, phase=started.current_phase),)


def text_wait_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    return state.none() if event.subagent else state.none(*text_wait_lines(WrittenWait.worded(event.call), settings))


def text_wait_lines(text: str, settings: Settings) -> tuple[Nudge, ...]:
    if not WrittenWait.is_written(text) or settings.value(WorkersOptions.MODE) != "orchestrator":
        return ()
    return (WorkersNudges.WAIT_TEXT.create(),)


def unmoved_task_lines(event: Ticked, settings: Settings) -> tuple[Nudge, ...]:
    if settings.value(WorkersOptions.MODE) != "orchestrator":
        return ()
    tasks = event.data.part(TasksPart)
    unmoved = tasks.last_moves
    if not unmoved:
        return ()
    long_unmoved = tuple(n for n, last_move in unmoved.items() if Timeout.minutes(settings.integer(WorkersOptions.STALLED_BLOCK_MINUTES)).started(last_move).is_elapsed(event.time))
    crowded = len(unmoved) > settings.decimal(WorkersOptions.BLOCKED_SHARE) * (tasks.open_count + len(unmoved))
    listed = tuple(sorted(unmoved)) if crowded else tuple(sorted(long_unmoved))
    return (WorkersNudges.UNMOVED_TASKS.create(tasks=", ".join(str(n) for n in listed)),) if listed else ()


def unordered_lines(event: Ticked, settings: Settings) -> tuple[Nudge, ...]:
    if settings.value(WorkersOptions.MODE) != "orchestrator":
        return ()
    least = settings.integer(WorkersOptions.UNORDERED_PLAN_TASKS)
    plans = event.data.part(PlansPart).started_plans if least else ()
    return tuple(WorkersNudges.UNLINKED_TASKS.create(plan=status.plan_id, open=status.total - status.done) for status in plans if status.total - status.done >= least and not status.blocked)


def report_mentions(data: FeatureData) -> list[Nudge]:
    workers = data.part(WorkersPart)
    summary = ", ".join(f"worker {w.id} ({w.name})" for w in workers.idle_workers)
    return [WorkersNudges.UNREAD_WORKER_REPORTS.create(reports_waiting=summary)] if summary else []


def worker_lines(event: ToolStarting, *verbs: str) -> list[WorkerLine]:
    return [line for part in event.call.parts if (line := WorkerLine.parsed(part.text)) and line.verb in verbs]


def idle_list(workers: tuple[Worker, ...]) -> str:
    return "\n".join(f"worker {w.id}, {w.name}, last on {w.files_line()}: `journal worker send {w.id} \"<job>\"`" for w in workers)



def profile_workers(workers: WorkersData, profile: str) -> list[Worker]:
    return [w for w in (*workers.dispatched_workers, *workers.idle_workers) if w.profile == profile]


def idle_offers(workers: WorkersData, line: WorkerLine) -> tuple[Worker, ...]:
    paths = PathMentions.build(line.brief)
    return tuple(sorted((w for w in workers.idle_workers if w.profile == line.profile), key=lambda w: not w.overlaps(paths)))


def idle_subagent_list(subagents: list[Subagent]) -> str:
    return "\n".join(f"subagent {s.id}, {s.agent_type}, on {s.task}: `SendMessage({{to: \"{s.session}\", message: \"<job>\"}})`" for s in subagents)


def is_reviewer(profile: str) -> bool:
    return any(role in profile for role in INDEPENDENT_ROLES)


def overlapping_workers(workers: WorkersData, brief: str) -> list[Worker]:
    paths = PathMentions.build(brief)
    return [w for w in reversed(workers.idle_workers) if w.overlaps(paths)]


def worktree_edits(workers: WorkersData, edited_paths: tuple[str, ...]):
    saved = [Path(p).expanduser().resolve() for p in edited_paths]
    contained = [p for p in saved if p.is_relative_to(workers.worktrees_root)]
    if not contained:
        return None
    folder = contained[0].relative_to(workers.worktrees_root).parts[0]
    return next((w for w in workers.worktrees if w.folder == folder), None)


def limit_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    if not isinstance(event.call.operation, SubagentDispatch) or event.subagent:
        return state.none()
    maximum, active = settings.integer(WorkersOptions.SUBAGENT_LIMIT), event.data.part(WorkersPart).active_subagents
    return state.refuse(WorkersNudges.SUBAGENT_OVERFLOW.create(running=active)) if maximum and active >= maximum else state.none()


def release_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    if settings.value(WorkersOptions.MODE) != "orchestrator" or settings.value(WorkersOptions.ORCHESTRATOR_RELEASES):
        return state.none()
    releases = ReleaseLines.found(tuple(part.text for part in event.call.parts))
    return state.refuse(WorkersNudges.RELEASE_REFUSED.create(line=releases[0])) if releases else state.none()


def worktrees_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    if event.subagent or not event.call.writes:
        return state.none()
    owner = worktree_edits(event.data.part(WorkersPart), event.call.edited_paths)
    return state.refuse(WorkersNudges.WORKER_FILE.create(n=owner.worker_id, name=owner.worker_name)) if owner else state.none()


def subagent_reuse_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    dispatch = event.call.operation
    if not isinstance(dispatch, SubagentDispatch):
        return state.none()
    matched = PathMentions.build(f"{dispatch.title} {dispatch.brief or ''}")
    if not matched or dispatch.role in INDEPENDENT_ROLES:
        return state.none()
    knowing = [s for s in reversed(event.data.part(WorkersPart).subagents) if s.is_idle() and s.agent_type == dispatch.role and PathOverlap.exists(PathMentions.build(s.brief), matched)]
    return state.refuse(WorkersNudges.SUBAGENT_REUSE.create(count=len(knowing), subagents=idle_subagent_list(knowing))) if knowing else state.none()


def files_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    knowing = [w for line in worker_lines(event, "dispatch") if not line.is_new_worker for w in overlapping_workers(event.data.part(WorkersPart), line.brief)]
    return state.refuse(WorkersNudges.WORKER_KNOWS_FILES.create(count=len(knowing), workers=idle_list(tuple(knowing)))) if knowing else state.none()


def idle_cap_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    lines = [line for line in worker_lines(event, "dispatch") if not is_reviewer(line.profile)]
    cap, workers = settings.integer(WorkersOptions.PROFILE_LIMIT) if lines else 0, event.data.part(WorkersPart)
    for line in lines if cap else []:
        members, offers = profile_workers(workers, line.profile), idle_offers(workers, line)
        if len(members) >= cap and offers:
            return state.refuse(WorkersNudges.IDLE_CAP.create(total=len(members), profile=line.profile, count=len(offers), workers=idle_list(offers)))
    return state.none()


def retire_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    lines = [line for line in worker_lines(event, "complete", "stop") if not line.reason]
    if not lines:
        return state.none()
    idle = {w.id: w for w in event.data.part(WorkersPart).idle_workers}
    retirements = [line for line in lines if line.number in idle]
    return state.refuse(WorkersNudges.REUSE_QUESTION.create(n=retirements[0].number, name=idle[retirements[0].number].name)) if retirements else state.none()


def open_work_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    workers = event.data.part(WorkersPart)
    if settings.value(WorkersOptions.MODE) != "orchestrator":
        return state.none()
    if is_full((*workers.dispatched_workers, *workers.ready_work), settings.integer(WorkersOptions.WORKER_LIMIT)):
        if not workers.ready_work:
            return state.none()
        return state.none(WorkersNudges.PLACES_FULL.create(n=min(workers.ready_work, key=lambda work: work.delivered_at).worker))
    return state.none()


def measure_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    if event.subagent or not settings.value(FitnessOptions.WARNINGS):
        return state.none()
    block = MeasureLines.block_lines(event.data, settings, event.time)
    if block and event.call.writes and not event.call.is_journal:
        return state.refuse(block[0])
    handover = any(part.text.startswith(command) for part in event.call.parts for command in HANDOVERS)
    dispatch = any(part.text.startswith(DISPATCH_COMMAND) for part in event.call.parts)
    return state.none(*MeasureLines.lines(event.data, settings), *(MeasureLines.handover_lines(event.data) if handover else ()), *(MeasureLines.dispatch_lines(event.data) if dispatch else ()))


def is_full(dispatched: tuple, limit: int) -> bool:
    return limit > 0 and len(dispatched) >= limit


DISPATCH_COMMAND = "journal worker dispatch"
HANDOVERS = {"journal worker dispatch": ("dispatch a worker", WorkersOptions.BUILDER_DISPATCH_ALLOWED), "journal worker queue": ("queue a worker's next task", WorkersOptions.BUILDER_QUEUE_ALLOWED)}


def capability_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    mode = settings.value(WorkersOptions.MODE)
    if event.subagent:
        return state.none()
    if isinstance(event.call.operation, SubagentDispatch):
        allowed = {"builder": WorkersOptions.BUILDER_SUBAGENTS_ALLOWED, "solo": WorkersOptions.SOLO_SUBAGENTS_ALLOWED}.get(mode)
        return state.refuse(WorkersNudges.MODE_REFUSAL.create(mode=mode, act="send subagents")) if allowed is not None and not settings.value(allowed) else state.none()
    if mode != "builder":
        return state.none()
    for part in event.call.parts:
        for command, (act, option) in HANDOVERS.items():
            if part.text.startswith(command) and not settings.value(option):
                return state.refuse(WorkersNudges.MODE_REFUSAL.create(mode=mode, act=act))
    return state.none()
