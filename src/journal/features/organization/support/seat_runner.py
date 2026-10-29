"""Run journal worker jobs inside their plan's persistent OpenRig Role seat."""

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from journal.config import Config
from journal.features.organization.support.caps import Caps
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.role_escalation import RoleEscalation
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.seat_runtime import SeatMember, SeatRuntime
from journal.features.organization.support.usage_ledger import UsageLedger
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.workers.workers_options import WorkersOptions
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.support.ref import Ref
from journal.models.worker import JOB_STARTS, Worker
from journal.models.worker_state import WorkerState
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.support.actor import Actor
from journal.support.process_check import ProcessCheck
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


POLL_SECONDS = 0.5
STARTUP_SECONDS = 45.0
IDLE_GRACE_SECONDS = 15.0
USAGE_POLL_SECONDS = 30.0
TIMEOUT_STATUS = -1
END_UNWATCHED = -2
ERROR_STATUS = -3


@dataclass(frozen=True)
class SeatJobIdentity:
    row_id: int
    worker_id: int
    generation: tuple[int, str, float] | None
    started_at: float = field(compare=False)

    @classmethod
    def from_worker(cls, worker: Worker) -> "SeatJobIdentity":
        generation = next(((index, move, time) for index, (move, time) in reversed(tuple(enumerate(worker.moves.steps)))
                           if move in JOB_STARTS), None)
        return cls(worker.row_id, worker.id, generation, worker.job_start_time() or worker.began)


class SeatRunner:
    """Run each plan Role in its persistent seat, and each many Role in its one-job seat."""

    def __init__(self, config: Config, organization: Organization, plans: Plans, workers: Workers,
                 environments: Environments, settings: SettingRows, scope: Scope,
                 runtime: SeatRuntime, ledger: UsageLedger, caps: Caps, tasks: Tasks, providers: Providers,
                 time_source: TimeSource, escalation: RoleEscalation, staffing: RigStaffing, branch: WorkerBranch) -> None:
        self.config, self.organization, self.plans = config, organization, plans
        self.workers, self.environments, self.settings, self.scope = workers, environments, settings, scope
        self.runtime, self.ledger, self.caps, self.time_source = runtime, ledger, caps, time_source
        self.tasks = tasks
        self.providers = providers
        self.escalation = escalation
        self.staffing = staffing
        self.branch = branch
        self._active: set[int] = set()
        self._active_jobs: dict[int, SeatJobIdentity] = {}
        self._finishing: set[SeatJobIdentity] = set()
        self._guard = threading.Lock()

    def applies(self, worker: Worker) -> bool:
        if not worker.role or not worker.plan_id or not worker.contract:
            return False
        role = self.organization.at(worker.contract).role(worker.role)
        plan = self.plans.find(worker.plan_id)
        return bool(role and plan.mode is PlanMode.ORGANIZATION and role.cardinality in (Cardinality.PLAN, Cardinality.MANY))

    def member(self, worker: Worker) -> SeatMember:
        plan = self.plans.find(worker.plan_id)
        rig_id = self.plans.rig_id(plan)
        if not rig_id:
            raise Rejection(f"plan {plan.id} has no OpenRig linked for Role {worker.role}")
        rig = self.staffing.find_rig(rig_id)
        role = self.organization.at(worker.contract).role(worker.role)
        if role is None:
            raise Rejection(f"the contract for plan {plan.id} no longer has Role {worker.role}")
        model = role.models.for_provider(worker.provider)
        if not model:
            raise Rejection(f"Role {worker.role} has no model selected for provider {worker.provider}")
        provider = self.providers.lookup(worker.provider)
        seat = self.staffing.role(plan, self.organization.at(worker.contract), role, worker.id, worker.provider,
                                  self.environments.find(worker.environment_id).name, self.branch.place(worker))
        member = self.runtime.member(rig.name, role.domain, seat.member, worker.provider)
        runtime = getattr(provider, "openrig_runtime", "")
        if runtime and member.runtime != runtime:
            raise Rejection(f"OpenRig seat {member.logical_id} does not use provider {worker.provider}'s runtime {runtime}")
        if member.provider != worker.provider or member.model != model or worker.model != model:
            raise Rejection(f"OpenRig seat {member.logical_id} does not use Role {worker.role}'s selected {worker.provider} model {model}")
        return member

    def retire(self, worker: Worker) -> None:
        if not worker.plan_id or not worker.contract:
            return
        contracts = self.organization.at(worker.contract)
        role = contracts.role(worker.role)
        if role is None or role.cardinality is not Cardinality.MANY:
            return
        self.staffing.remove_role(self.plans.find(worker.plan_id), contracts, role, worker.id, worker.provider)

    def start(self, worker: Worker, actor: Actor, prompt: str,
              ended: Callable[[Worker, SeatJobIdentity, int, Actor], None]) -> None:
        identity = SeatJobIdentity.from_worker(worker)
        send_existing = False
        with self._guard:
            if worker.id in self._active:
                if self._active_jobs.get(worker.id) == identity:
                    return
                self._active_jobs[worker.id] = identity
                send_existing = True
            else:
                self._active.add(worker.id)
                self._active_jobs[worker.id] = identity
        target = self.send_existing if send_existing else self.scoped
        threading.Thread(target=target, args=(worker, identity, actor, prompt, ended), name=f"seat-worker-{worker.id}", daemon=True).start()

    def scoped(self, worker: Worker, identity: SeatJobIdentity, actor: Actor, prompt: str,
               ended: Callable[[Worker, SeatJobIdentity, int, Actor], None]) -> None:
        try:
            with self.scope.environment(worker.environment_id):
                self.run(worker, identity, actor, prompt, ended)
        except Rejection as failure:
            self.fail(worker, identity, actor, ended, failure)
        finally:
            self.release(identity)

    def send_existing(self, worker: Worker, identity: SeatJobIdentity, actor: Actor, prompt: str,
                      ended: Callable[[Worker, SeatJobIdentity, int, Actor], None]) -> None:
        try:
            with self.scope.environment(worker.environment_id):
                current = self.current_job(identity)
                if current is None or current.state not in (WorkerState.DISPATCHED, WorkerState.READY):
                    return
                member = self.member(worker)
                self.runtime.check_version(member.openrig_version)
                environment = self.environments.find(worker.environment_id).name
                token = self.runtime.worker_token(member, worker.provider, member.model, Actor.worker(worker.id).stamp, environment)
                session = self.runtime.session(member, worker.resume)
                if session is None or not ProcessCheck.is_running(session.pid):
                    raise Rejection(f"OpenRig seat {member.target} stopped before worker {worker.id}'s next job was sent")
                current = self.current_job(identity)
                if current is None or current.state not in (WorkerState.DISPATCHED, WorkerState.READY):
                    return
                current = self.workers.save(current.with_(session=session.session, resume=session.session, token_hash=token.digest(), pid=session.pid, began=self.time_source.seconds()), actor)
                deadline = time.monotonic() + STARTUP_SECONDS
                while True:
                    if self.current_job(identity) is None:
                        return
                    try:
                        self.runtime.send(member, prompt)
                        break
                    except Rejection:
                        if time.monotonic() >= deadline:
                            raise
                        time.sleep(POLL_SECONDS)
                self.monitor(current, identity, member, session.session, actor, ended, identity.started_at or current.began)
        except Rejection as failure:
            self.fail(worker, identity, actor, ended, failure)
        finally:
            self.release(identity)

    def run(self, worker: Worker, identity: SeatJobIdentity, actor: Actor, prompt: str,
            ended: Callable[[Worker, SeatJobIdentity, int, Actor], None]) -> None:
        member = self.member(worker)
        self.runtime.check_version(member.openrig_version)
        environment = self.environments.find(worker.environment_id).name
        token = self.runtime.worker_token(member, worker.provider, member.model, Actor.worker(worker.id).stamp, environment)
        capacity_notified = False
        while not self.capacity_available(worker):
            if not capacity_notified:
                self.escalation.seat_cap_waiting(worker, "it will resume when a seat is free", Actor.system())
                capacity_notified = True
            time.sleep(POLL_SECONDS)
            current = self.current_job(identity)
            if current is None:
                return
            if current.state not in (WorkerState.DISPATCHED, WorkerState.READY):
                self.preserve(current, actor, identity)
                return
        if self.current_job(identity) is None:
            return
        session = self.runtime.session(member, worker.resume)
        if session is None:
            if worker.resume:
                raise Rejection(f"OpenRig seat {member.target} stopped; this version cannot resume the session, so it was left unchanged")
            self.runtime.launch(member, f"journal worker {worker.id} starts task {identity.started_at or self.time_source.seconds()}")
            deadline = time.monotonic() + STARTUP_SECONDS
            while session is None and time.monotonic() < deadline:
                time.sleep(POLL_SECONDS)
                if self.current_job(identity) is None:
                    return
                session = self.runtime.session(member)
            if session is None:
                raise Rejection(f"OpenRig seat {member.target} did not report a live native session after launch")
        if not ProcessCheck.is_running(session.pid):
            raise Rejection(f"OpenRig seat {member.target} has no live {member.provider} process")
        current = self.current_job(identity)
        if current is None:
            return
        started_at = self.time_source.seconds()
        current = self.workers.save(current.with_(session=session.session, resume=session.session, token_hash=token.digest(), pid=session.pid, began=started_at), actor)
        deadline = time.monotonic() + STARTUP_SECONDS
        while True:
            if self.current_job(identity) is None:
                return
            try:
                self.runtime.send(member, prompt)
                break
            except Rejection:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(POLL_SECONDS)
        self.monitor(current, identity, member, session.session, actor, ended, identity.started_at or started_at)

    def monitor(self, worker: Worker, identity: SeatJobIdentity, member: SeatMember, native_session: str,
                actor: Actor, ended: Callable[[Worker, SeatJobIdentity, int, Actor], None], started_at: float) -> None:
        usage_at = 0.0
        while True:
            time.sleep(POLL_SECONDS)
            current = self.current_job(identity)
            if current is None:
                return
            if current.state not in (WorkerState.DISPATCHED, WorkerState.READY):
                if current.state != WorkerState.STOPPED:
                    self.record_usage(current, member, native_session, self.time_source.seconds(), actor)
                self.finish_once(worker, identity, 0, actor, ended)
                return
            if not self.tasks.holder_task_ids(Ref.build(current)) and self.tasks.finished_task_ids(Ref.build(current)):
                self.finish_once(current, identity, 0, actor, ended)
                return
            now = self.time_source.seconds()
            job_started = identity.started_at or started_at
            timeout = self.settings.decimal(WorkersOptions.TIMEOUT) * 60
            if timeout and now - job_started >= timeout:
                self.runtime.stop(member.target, f"journal worker {worker.id} reached its job time limit")
                self.finish_once(current, identity, TIMEOUT_STATUS, actor, ended)
                return
            session = self.runtime.session(member, native_session)
            if current.pid <= 0 and session is not None and ProcessCheck.is_running(session.pid):
                current = self.current_job(identity)
                if current is None:
                    return
                current = self.workers.save(current.with_(pid=session.pid, session=session.session, resume=session.session,
                                                           token_hash=current.token_hash or worker.token_hash,
                                                           began=current.began or started_at), actor)
            if current.pid <= 0:
                if now - job_started <= STARTUP_SECONDS:
                    continue
                self.finish_once(current, identity, END_UNWATCHED, actor, ended)
                return
            if not ProcessCheck.is_running(current.pid) or session is None:
                self.finish_once(current, identity, END_UNWATCHED, actor, ended)
                return
            activity_status, updated_at = session.activity_status, session.status_updated_at
            if activity_status in {"idle", "stopped", "ended"} and updated_at > job_started and now - job_started > IDLE_GRACE_SECONDS:
                self.finish_once(current, identity, END_UNWATCHED, actor, ended)
                return
            if now - usage_at >= USAGE_POLL_SECONDS:
                self.record_usage(current, member, native_session, now, actor)
                usage_at = now

    def record_usage(self, worker: Worker, member: SeatMember, native_session: str, now: float, actor: Actor) -> None:
        plan_id = worker.plan_id
        estimate = None
        if plan_id:
            reading = self.runtime.usage_cost(member.target)
            estimate = self.ledger.record(plan_id, member.target, native_session, reading, now,
                                          self.runtime.expected_seats(member.rig))
        source = f"{worker.provider} journal status files"
        try:
            windows = self.providers.lookup(worker.provider).status(native_session, self.config.status_home).windows
        except Rejection:
            windows = None
        if windows:
            self.ledger.record_subscription_limits(
                {window.key: {"used_percentage": window.used, "resets_at": window.resets_at} for window in windows},
                source,
                ", ".join(window.label for window in windows),
                now,
                "account-wide subscription windows",
            )
        else:
            self.ledger.record_subscription_limits(None, source, "account-wide subscription windows", now, "account-wide subscription windows")
        if estimate is not None:
            decision = self.caps.plan_cost(estimate)
            if decision.status == "exceeded":
                self.escalation.cap_reached(worker, decision.reason, Actor.system())
                plan = self.plans.find(plan_id)
                if plan.state in (PlanState.STARTED, PlanState.DELEGATED):
                    self.plans.postpone(plan, Actor.system())
                self.runtime.stop(member.target, decision.reason)
                raise Rejection(decision.reason)

    def is_finished(self, worker: Worker, actor: Actor, ended: Callable[[Worker, SeatJobIdentity, int, Actor], None]) -> bool:
        identity = SeatJobIdentity.from_worker(worker)
        current = self.current_job(identity)
        if current is None:
            return True
        if current.state not in (WorkerState.DISPATCHED, WorkerState.READY):
            self.preserve(worker, actor, identity)
            return True
        if current.pid <= 0:
            return False
        if not ProcessCheck.is_running(current.pid):
            self.finish_once(current, identity, END_UNWATCHED, actor, ended)
            return True
        limit = self.settings.decimal(WorkersOptions.TIMEOUT) * 60
        job_started = identity.started_at or current.began
        if limit and job_started and self.time_source.seconds() - job_started >= limit:
            try:
                self.runtime.stop(self.member(current).target, f"journal worker {worker.id} reached its job time limit")
            except Rejection:
                pass
            self.finish_once(current, identity, TIMEOUT_STATUS, actor, ended)
            return True
        member = self.member(current)
        session = self.runtime.session(member, current.resume)
        if session is None:
            self.finish_once(current, identity, END_UNWATCHED, actor, ended)
            return True
        activity_status, updated_at = session.activity_status, session.status_updated_at
        if activity_status in {"idle", "stopped", "ended"} and updated_at > job_started and job_started and self.time_source.seconds() - job_started > IDLE_GRACE_SECONDS:
            self.finish_once(current, identity, END_UNWATCHED, actor, ended)
            return True
        return False

    def capacity_available(self, worker: Worker) -> bool:
        limit = self.settings.integer(OrganizationOptions.SEAT_CAP)
        if not limit:
            return True
        with self._guard:
            starting = set(self._active)
        active = sum(1 for row in self.workers.all_dispatched() if row.id != worker.id and self.applies(row)
                     and (row.id in starting or row.pid > 0 and ProcessCheck.is_running(row.pid)))
        return self.caps.seats(active).allowed

    def is_seat_pid(self, pid: int) -> bool:
        return pid > 0 and any(row.pid == pid and self.applies(row) for row in self.workers.scoped())

    def recover(self, worker: Worker, actor: Actor, prompt: str,
                ended: Callable[[Worker, SeatJobIdentity, int, Actor], None]) -> None:
        if worker.state not in (WorkerState.DISPATCHED, WorkerState.READY):
            return
        if worker.pid <= 0:
            self.start(worker, actor, prompt, ended)
            return
        identity = SeatJobIdentity.from_worker(worker)
        with self._guard:
            if worker.id in self._active:
                return
            self._active.add(worker.id)
            self._active_jobs[worker.id] = identity
        threading.Thread(target=self.monitor_existing, args=(worker, identity, actor, ended), name=f"seat-recovery-{worker.id}", daemon=True).start()

    def monitor_existing(self, worker: Worker, identity: SeatJobIdentity, actor: Actor,
                         ended: Callable[[Worker, SeatJobIdentity, int, Actor], None]) -> None:
        try:
            with self.scope.environment(worker.environment_id):
                if self.current_job(identity) is None:
                    return
                member = self.member(worker)
                self.runtime.check_version(member.openrig_version)
                session = self.runtime.session(member, worker.resume)
                if session is None or session.pid != worker.pid:
                    self.finish_once(worker, identity, END_UNWATCHED, actor, ended)
                    return
                self.monitor(worker, identity, member, session.session, actor, ended, identity.started_at or worker.began)
        except Rejection as failure:
            self.fail(worker, identity, actor, ended, failure)
        finally:
            self.release(identity)

    def stop(self, worker: Worker, reason: str) -> None:
        if worker.role and worker.plan_id:
            self.runtime.stop(self.member(worker).target, reason)

    def preserve(self, worker: Worker, actor: Actor, identity: SeatJobIdentity | None = None) -> None:
        if worker.pid > 0 and worker.token_hash:
            current = self.workers.find(worker.row_id)
            if current.state == WorkerState.STOPPED or identity and SeatJobIdentity.from_worker(current) != identity:
                return
            if (current.pid, current.token_hash, current.session, current.resume) != (worker.pid, worker.token_hash, worker.session, worker.resume):
                self.workers.save(current.with_(pid=worker.pid, token_hash=worker.token_hash, session=worker.session, resume=worker.resume), actor)

    def current_job(self, identity: SeatJobIdentity) -> Worker | None:
        current = self.workers.find(identity.row_id)
        return current if SeatJobIdentity.from_worker(current) == identity else None

    def release(self, identity: SeatJobIdentity) -> None:
        with self._guard:
            if self._active_jobs.get(identity.worker_id) == identity:
                self._active.discard(identity.worker_id)
                self._active_jobs.pop(identity.worker_id, None)

    def finish_once(self, worker: Worker, identity: SeatJobIdentity, code: int, actor: Actor,
                    ended: Callable[[Worker, SeatJobIdentity, int, Actor], None]) -> None:
        with self._guard:
            if identity in self._finishing or self.current_job(identity) is None:
                return
            self._finishing.add(identity)
        try:
            ended(worker, identity, code, actor)
        finally:
            with self._guard:
                self._finishing.discard(identity)

    def fail(self, worker: Worker, identity: SeatJobIdentity, actor: Actor,
             ended: Callable[[Worker, SeatJobIdentity, int, Actor], None], failure: Exception) -> None:
        if self.current_job(identity) is None:
            return
        error = self.config.home / "runtime" / "workers" / f"{worker.id}.err"
        error.parent.mkdir(parents=True, exist_ok=True)
        error.write_text(str(failure))
        current = self.current_job(identity)
        if current is not None:
            self.finish_once(current, identity, ERROR_STATUS, actor, ended)

