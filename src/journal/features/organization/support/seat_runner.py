"""Run journal worker jobs inside their plan's persistent OpenRig Role seat."""

import threading
import time
from collections.abc import Callable

from journal.config import Config
from journal.features.organization.support.caps import Caps
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.seat_runtime import SeatMember, SeatRuntime
from journal.features.organization.support.usage_ledger import UsageLedger
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.workers.workers_options import WorkersOptions
from journal.models.plan_state import PlanState
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.rigs import Rigs
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
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


class SeatRunner:
    """Use RigSpecs' selected-provider member and OpenRig delivery; never spawn a second agent."""

    def __init__(self, config: Config, organization: Organization, plans: Plans, rigs: Rigs, workers: Workers,
                 environments: Environments, settings: SettingRows, scope: Scope,
                 runtime: SeatRuntime, ledger: UsageLedger, caps: Caps, tasks: Tasks, providers: Providers, time_source: TimeSource) -> None:
        self.config, self.organization, self.plans, self.rigs = config, organization, plans, rigs
        self.workers, self.environments, self.settings, self.scope = workers, environments, settings, scope
        self.runtime, self.ledger, self.caps, self.time_source = runtime, ledger, caps, time_source
        self.tasks = tasks
        self.providers = providers
        self._active: set[int] = set()
        self._active_jobs: dict[int, float] = {}
        self._finishing: set[int] = set()
        self._guard = threading.Lock()

    def applies(self, worker: Worker) -> bool:
        if not worker.role or not worker.plan_id or not worker.contract:
            return False
        role = self.organization.at(worker.contract).role(worker.role)
        return bool(role and role.cardinality.value == "plan")

    def member(self, worker: Worker) -> SeatMember:
        plan = self.plans.find(worker.plan_id)
        rig_id = self.plans.rig_id(plan)
        if not rig_id:
            raise Rejection(f"plan {plan.id} has no OpenRig linked for Role {worker.role}")
        rig = self.rigs.find(rig_id)
        role = self.organization.at(worker.contract).role(worker.role)
        if role is None:
            raise Rejection(f"the contract for plan {plan.id} no longer has Role {worker.role}")
        model = role.models.for_provider(worker.provider)
        if not model:
            raise Rejection(f"Role {worker.role} has no model selected for provider {worker.provider}")
        provider = self.providers.lookup(worker.provider)
        member = self.runtime.member(rig.name, role.domain, role.id, worker.provider)
        runtime = getattr(provider, "openrig_runtime", "")
        if runtime and member.runtime != runtime:
            raise Rejection(f"OpenRig seat {member.logical_id} does not use provider {worker.provider}'s runtime {runtime}")
        if member.provider != worker.provider or member.model != model or worker.model != model:
            raise Rejection(f"OpenRig seat {member.logical_id} does not use Role {worker.role}'s selected {worker.provider} model {model}")
        return member

    def start(self, worker: Worker, actor: Actor, prompt: str, ended: Callable[[Worker, int, Actor], None]) -> None:
        job_started = worker.job_start_time() or worker.began
        send_existing = False
        with self._guard:
            if worker.id in self._active:
                if self._active_jobs.get(worker.id) == job_started:
                    return
                self._active_jobs[worker.id] = job_started
                send_existing = True
            else:
                self._active.add(worker.id)
                self._active_jobs[worker.id] = job_started
        target = self.send_existing if send_existing else self.scoped
        threading.Thread(target=target, args=(worker, actor, prompt, ended), name=f"seat-worker-{worker.id}", daemon=True).start()

    def scoped(self, worker: Worker, actor: Actor, prompt: str, ended: Callable[[Worker, int, Actor], None]) -> None:
        try:
            with self.scope.environment(worker.environment_id):
                self.run(worker, actor, prompt, ended)
        except Rejection as failure:
            self.fail(worker, actor, ended, failure)
        finally:
            with self._guard:
                self._active.discard(worker.id)
                self._active_jobs.pop(worker.id, None)

    def send_existing(self, worker: Worker, actor: Actor, prompt: str, ended: Callable[[Worker, int, Actor], None]) -> None:
        try:
            with self.scope.environment(worker.environment_id):
                member = self.member(worker)
                self.runtime.check_version(member.openrig_version)
                environment = self.environments.find(worker.environment_id).name
                token = self.runtime.worker_token(member, worker.provider, member.model, Actor.worker(worker.id).stamp, environment)
                session = self.runtime.session(member, worker.resume)
                if session is None or not ProcessCheck.is_running(session.pid):
                    raise Rejection(f"OpenRig seat {member.target} stopped before worker {worker.id}'s next job was sent")
                current = self.workers.find(worker.row_id)
                if current.state not in (WorkerState.DISPATCHED, WorkerState.READY):
                    return
                current = self.workers.save(current.with_(session=session.session, resume=session.session, token_hash=token.digest(), pid=session.pid, began=self.time_source.seconds()), actor)
                deadline = time.monotonic() + STARTUP_SECONDS
                while True:
                    try:
                        self.runtime.send(member, prompt)
                        return
                    except Rejection:
                        if time.monotonic() >= deadline:
                            raise
                        time.sleep(POLL_SECONDS)
        except Rejection as failure:
            self.fail(worker, actor, ended, failure)

    def run(self, worker: Worker, actor: Actor, prompt: str, ended: Callable[[Worker, int, Actor], None]) -> None:
        member = self.member(worker)
        self.runtime.check_version(member.openrig_version)
        environment = self.environments.find(worker.environment_id).name
        token = self.runtime.worker_token(member, worker.provider, member.model, Actor.worker(worker.id).stamp, environment)
        while not self.capacity_available(worker):
            time.sleep(POLL_SECONDS)
            current = self.workers.find(worker.row_id)
            if current.state not in (WorkerState.DISPATCHED, WorkerState.READY):
                self.preserve(current, actor)
                return
        session = self.runtime.session(member, worker.resume)
        if session is None:
            if worker.resume:
                raise Rejection(f"OpenRig seat {member.target} stopped; this OpenRig version cannot resume its native session, so it was not replaced with a blank one")
            self.runtime.launch(member, f"journal worker {worker.id} starts task {worker.job_start_time() or self.time_source.seconds()}")
            deadline = time.monotonic() + STARTUP_SECONDS
            while session is None and time.monotonic() < deadline:
                time.sleep(POLL_SECONDS)
                session = self.runtime.session(member)
            if session is None:
                raise Rejection(f"OpenRig seat {member.target} did not report a live native session after launch")
        if not ProcessCheck.is_running(session.pid):
            raise Rejection(f"OpenRig seat {member.target} has no live {member.provider} process")
        current = self.workers.find(worker.row_id)
        started_at = self.time_source.seconds()
        current = self.workers.save(current.with_(session=session.session, resume=session.session, token_hash=token.digest(), pid=session.pid, began=started_at), actor)
        deadline = time.monotonic() + STARTUP_SECONDS
        while True:
            try:
                self.runtime.send(member, prompt)
                break
            except Rejection:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(POLL_SECONDS)
        self.monitor(current, member, session.session, actor, ended, started_at)

    def monitor(self, worker: Worker, member: SeatMember, native_session: str, actor: Actor,
                ended: Callable[[Worker, int, Actor], None], started_at: float) -> None:
        usage_at = 0.0
        while True:
            time.sleep(POLL_SECONDS)
            current = self.workers.find(worker.row_id)
            if current.state not in (WorkerState.DISPATCHED, WorkerState.READY):
                self.record_usage(current, member, native_session, self.time_source.seconds(), actor)
                self.finish_once(worker, 0, actor, ended)
                return
            if not self.tasks.holder_task_ids(Ref.build(current)) and self.tasks.finished_task_ids(Ref.build(current)):
                self.finish_once(current, 0, actor, ended)
                return
            now = self.time_source.seconds()
            job_started = current.job_start_time() or started_at
            timeout = self.settings.decimal(WorkersOptions.TIMEOUT) * 60
            if timeout and now - job_started >= timeout:
                self.runtime.stop(member.target, f"journal worker {worker.id} reached its job time limit")
                self.finish_once(current, TIMEOUT_STATUS, actor, ended)
                return
            session = self.runtime.session(member, native_session)
            if current.pid <= 0 and session is not None and ProcessCheck.is_running(session.pid):
                current = self.workers.save(current.with_(pid=session.pid, session=session.session, resume=session.session,
                                                           token_hash=current.token_hash or worker.token_hash,
                                                           began=current.began or started_at), actor)
            if current.pid <= 0:
                if now - job_started <= STARTUP_SECONDS:
                    continue
                self.finish_once(current, END_UNWATCHED, actor, ended)
                return
            if not ProcessCheck.is_running(current.pid) or session is None:
                self.finish_once(current, END_UNWATCHED, actor, ended)
                return
            try:
                status = self.runtime.status(member.target)
            except Rejection:
                status = {}
            session_status = self.runtime.session_status(status)
            if session_status in {"idle", "stopped", "ended"} and now - job_started > IDLE_GRACE_SECONDS:
                self.finish_once(current, END_UNWATCHED, actor, ended)
                return
            if now - usage_at >= USAGE_POLL_SECONDS:
                self.record_usage(current, member, native_session, now, actor)
                usage_at = now

    def record_usage(self, worker: Worker, member: SeatMember, native_session: str, now: float, actor: Actor) -> None:
        plan_id = worker.plan_id
        amount = self.runtime.cumulative_cost(member.target)
        if plan_id and amount is not None:
            estimate = self.ledger.observe(plan_id, member.target, native_session, amount, now, self.runtime.expected_seats(member.rig))
            decision = self.caps.plan_cost(estimate)
            if decision.status == "exceeded":
                plan = self.plans.find(plan_id)
                if plan.state in (PlanState.STARTED, PlanState.DELEGATED):
                    self.plans.postpone(plan, Actor.system())
                self.runtime.stop(member.target, "the plan's estimated OpenRig usage reached its configured cap")
                raise Rejection(decision.reason)
        source = f"{worker.provider} journal status files"
        windows = self.providers.lookup(worker.provider).status(native_session, self.config.status_home).windows
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

    def is_finished(self, worker: Worker, actor: Actor, ended: Callable[[Worker, int, Actor], None]) -> bool:
        if worker.state not in (WorkerState.DISPATCHED, WorkerState.READY):
            self.preserve(worker, actor)
            return True
        if worker.pid <= 0:
            return False
        if not ProcessCheck.is_running(worker.pid):
            self.finish_once(worker, END_UNWATCHED, actor, ended)
            return True
        limit = self.settings.decimal(WorkersOptions.TIMEOUT) * 60
        job_started = worker.job_start_time() or worker.began
        if limit and job_started and self.time_source.seconds() - job_started >= limit:
            try:
                self.runtime.stop(self.member(worker).target, f"journal worker {worker.id} reached its job time limit")
            except Rejection:
                pass
            self.finish_once(worker, TIMEOUT_STATUS, actor, ended)
            return True
        member = self.member(worker)
        session = self.runtime.session(member, worker.resume)
        if session is None:
            self.finish_once(worker, END_UNWATCHED, actor, ended)
            return True
        try:
            status = self.runtime.status(member.target)
        except Rejection:
            return False
        session_status = self.runtime.session_status(status)
        if session_status in {"idle", "stopped", "ended"} and job_started and self.time_source.seconds() - job_started > IDLE_GRACE_SECONDS:
            self.finish_once(worker, END_UNWATCHED, actor, ended)
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

    def recover(self, worker: Worker, actor: Actor, prompt: str, ended: Callable[[Worker, int, Actor], None]) -> None:
        if worker.state not in (WorkerState.DISPATCHED, WorkerState.READY):
            return
        if worker.pid <= 0:
            self.start(worker, actor, prompt, ended)
            return
        job_started = worker.job_start_time() or worker.began
        with self._guard:
            if worker.id in self._active:
                return
            self._active.add(worker.id)
            self._active_jobs[worker.id] = job_started
        threading.Thread(target=self.monitor_existing, args=(worker, actor, ended), name=f"seat-recovery-{worker.id}", daemon=True).start()

    def monitor_existing(self, worker: Worker, actor: Actor, ended: Callable[[Worker, int, Actor], None]) -> None:
        try:
            with self.scope.environment(worker.environment_id):
                member = self.member(worker)
                self.runtime.check_version(member.openrig_version)
                session = self.runtime.session(member, worker.resume)
                if session is None or session.pid != worker.pid:
                    self.finish_once(worker, END_UNWATCHED, actor, ended)
                    return
                self.monitor(worker, member, session.session, actor, ended, worker.job_start_time() or worker.began)
        except Rejection as failure:
            self.fail(worker, actor, ended, failure)
        finally:
            with self._guard:
                self._active.discard(worker.id)
                self._active_jobs.pop(worker.id, None)

    def stop(self, worker: Worker, reason: str) -> None:
        if worker.role and worker.plan_id:
            self.runtime.stop(self.member(worker).target, reason)

    def preserve(self, worker: Worker, actor: Actor) -> None:
        if worker.pid > 0 and worker.token_hash:
            current = self.workers.find(worker.row_id)
            if (current.pid, current.token_hash, current.session, current.resume) != (worker.pid, worker.token_hash, worker.session, worker.resume):
                self.workers.save(current.with_(pid=worker.pid, token_hash=worker.token_hash, session=worker.session, resume=worker.resume), actor)

    def finish_once(self, worker: Worker, code: int, actor: Actor, ended: Callable[[Worker, int, Actor], None]) -> None:
        with self._guard:
            if worker.id in self._finishing:
                return
            self._finishing.add(worker.id)
        try:
            ended(worker, code, actor)
        finally:
            with self._guard:
                self._finishing.discard(worker.id)

    def fail(self, worker: Worker, actor: Actor, ended: Callable[[Worker, int, Actor], None], failure: Exception) -> None:
        error = self.config.home / "runtime" / "workers" / f"{worker.id}.err"
        error.parent.mkdir(parents=True, exist_ok=True)
        error.write_text(str(failure))
        current = self.workers.find(worker.row_id)
        self.finish_once(current, ERROR_STATUS, actor, ended)

