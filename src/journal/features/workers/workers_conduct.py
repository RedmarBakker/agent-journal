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
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.events.rows.worker_ready import WorkerReady
from journal.events.rows.worker_unfinished import WorkerUnfinished
from journal.events.rows.worker_reported import WorkerReported
from journal.events.rows.worker_stopped import WorkerStopped
from journal.events.rows.worker_merged import WorkerMerged
from journal.events.rows.worker_retired import WorkerRetired
from journal.events.rows.worker_mention import WorkerMention
from journal.events.rows.worker_dispatched import WorkerDispatched
from journal.features.workers.support.worker_line import WorkerLine
from journal.features.workers.support.path_mentions import PathMentions
from journal.models.subagent import Subagent
from journal.models.support.path_overlap import PathOverlap
from journal.models.worker import Worker
from journal.features.workers.support.workers_data import WorkersData
from journal.support.subagent_dispatch import SubagentDispatch
from journal.features.tasks.tasks_part import TasksPart
from journal.features.workers.workers_alignments import WorkersAlignments
from journal.features.workers.workers_profiles import WorkersProfiles
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions
from journal.features.workers.workers_part import WorkersPart
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.reviewing.reviewing_options import ReviewingOptions

INDEPENDENT_ROLES = ("auditor", "reviewer", "plan-reviewer", "critic")


class WorkersConduct(Conduct):
    """The workers feature's conduct in every state: a subagent past the most allowed at once is blocked, a write into a worker's worktree is blocked, a new subagent whose job names files an idle one of the same kind worked on is blocked in favour of those, unless they are retired, a dispatch whose brief names files an idle worker touched is blocked in favour of that worker, a dispatch past its profile's stored workers is blocked while one of them is idle, retiring an idle worker is blocked until the repeat says why it cannot be reused, the reports not acted on are named at a stop and on the tick, work waiting to be checked is named again every so many tool uses, a worker of this agent's silent for twenty minutes is named once on the tick, a worker this agent dispatches pushes Awaiting on its work, and a worker's report is informed as it comes."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        checks = (subagent_reuse_check, limit_check, worktrees_check, files_check, idle_cap_check, retire_check, open_work_check, waiting_work_check, alignment_check)
        return Transition.merged(self, [check(self, event, settings) for check in checks])

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.none(*report_mentions(event.data), *check_reminders(event.data, event.time))

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        workers = event.data.part(WorkersPart)
        silent = [WorkersNudges.SILENT_WORKER.create(n=w.id, name=w.name, minutes=w.silence.minutes()) for w in workers.dispatched_workers if w.dispatcher == event.session and w.is_silent(event.time)]
        return self.none(*report_mentions(event.data), *check_reminders(event.data, event.time), *silent)

    def on_worker_dispatched(self, event: WorkerDispatched, settings: Settings) -> Transition:
        return self.push(ExternalWait.opened(*event.wait_terms())) if event.awaiter == event.session else self.none()

    def on_worker_unfinished(self, event: WorkerUnfinished, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(WorkersNudges.RUN_UNFINISHED.create(n=event.worker.id, name=event.worker.name))

    def on_worker_delivered(self, event: WorkerDelivered, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        ready = [work for work in event.data.part(WorkersPart).ready_work if work.worker == event.worker.id]
        return self.none(*(WorkersNudges.WORK_READY.create(n=work.worker, name=work.name, task=work.task) for work in ready))

    def on_worker_ready(self, event: WorkerReady, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(WorkersNudges.WORKER_ARRIVAL.create(n=event.worker.id, name=event.worker.name))

    def on_worker_reported(self, event: WorkerReported, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(WorkersNudges.WORKER_REPORTED.create(n=event.worker.id, name=event.worker.name))

    def on_worker_stopped(self, event: WorkerStopped, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(WorkersNudges.WORKER_STOPPED_UNREPORTED.create(n=event.worker.id, name=event.worker.name), *free_place(event.worker, event.data, settings))

    def on_worker_merged(self, event: WorkerMerged, settings: Settings) -> Transition:
        return place_answer(self, event, settings)

    def on_worker_retired(self, event: WorkerRetired, settings: Settings) -> Transition:
        return place_answer(self, event, settings)


def report_mentions(data: FeatureData) -> list[Nudge]:
    workers = data.part(WorkersPart)
    summary = ", ".join(f"worker {w.id} ({w.name})" for w in workers.idle_workers)
    return [WorkersNudges.UNREAD_WORKER_REPORTS.create(reports_waiting=summary)] if summary else []


def check_reminders(data: FeatureData, time: float) -> list[Nudge]:
    reminder = WorkersNudges.CHECK_REMINDER
    ready = data.part(WorkersPart).ready_work
    return [reminder.create(n=work.worker, name=work.name, task=work.task) for work in ready if work.is_waiting(time, reminder.repeat.amount)]


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
            return state.refuse(WorkersNudges.IDLE_CAP.create(kept=len(members), profile=line.profile, count=len(offers), workers=idle_list(offers)))
    return state.none()


def retire_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    lines = [line for line in worker_lines(event, "complete", "stop") if not line.reason]
    if not lines:
        return state.none()
    idle = {w.id: w for w in event.data.part(WorkersPart).idle_workers}
    retirements = [line for line in lines if line.number in idle]
    return state.refuse(WorkersNudges.REUSE_QUESTION.create(n=retirements[0].number, name=idle[retirements[0].number].name)) if retirements else state.none()


def open_work_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    tasks, workers = event.data.part(TasksPart), event.data.part(WorkersPart)
    if settings.value(WorkersOptions.MODE) != "orchestrator" or is_full(workers.dispatched_workers, settings.integer(WorkersOptions.WORKER_LIMIT)) or not tasks.open_ids:
        return state.none()
    return state.none(WorkersNudges.CREW_REMINDER.create(count=tasks.open_count, tasks=tasks.open_next))


def waiting_work_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    span = Timeout.tool_uses(settings.integer(WorkersOptions.CHECK_REMINDER_USES))
    if event.subagent or not span.amount or not span.started(0).is_period_start(event.tool_use):
        return state.none()
    ready = event.data.part(WorkersPart).ready_work
    return state.none(*(WorkersNudges.CHECK_REMINDER.create(n=work.worker, name=work.name, task=work.task) for work in ready))


def free_place(worker: WorkerMention, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
    tasks = data.part(TasksPart)
    if settings.value(WorkersOptions.MODE) != "orchestrator" or not tasks.open_ids:
        return ()
    return (WorkersNudges.PLACE_FREE.create(n=worker.id, name=worker.name, count=tasks.open_count, tasks=tasks.open_next),)


def place_answer(state: BaseState, event: WorkerMerged | WorkerRetired, settings: Settings) -> Transition:
    return state.none() if event.worker.is_other_dispatcher(event.session) else state.none(*free_place(event.worker, event.data, settings))


def alignment_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    if event.subagent:
        return state.none()
    mode, workers = str(settings.value(WorkersOptions.MODE)), event.data.part(WorkersPart)
    return state.none(*(line for alignment in WorkersAlignments.ALL if (line := alignment.line(mode, workers, settings))), *fitness_lines(mode, workers, settings))


def fitness_lines(mode: str, workers, settings: Settings) -> tuple[Nudge, ...]:
    profile, threshold = (WorkersProfiles.reviewed_mode_profile if settings.value(ReviewingOptions.REVIEWER) else WorkersProfiles.mode_profile)(mode), settings.integer(WorkersOptions.FITNESS_THRESHOLD)
    if profile is None or threshold <= 0:
        return ()
    fitness = profile.scored(workers.tool_uses)
    if not fitness.is_measured or fitness.score >= threshold:
        return ()
    return (WorkersNudges.FITNESS_LOW.create(mode=mode, score=fitness.score, gaps=" ".join(f"{gap.text()}." for gap in fitness.gaps)),)


def is_full(dispatched: tuple, limit: int) -> bool:
    return limit > 0 and len(dispatched) >= limit
