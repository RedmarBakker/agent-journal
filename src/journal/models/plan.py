from dataclasses import dataclass
from typing import ClassVar

from journal.models.plan_state import PlanState
from journal.events.rows.plan_abandoned import PlanAbandoned
from journal.events.rows.plan_approved import PlanApproved
from journal.events.rows.plan_reviewed import PlanReviewed
from journal.events.rows.plan_blocked import PlanBlocked
from journal.events.rows.plan_postponed import PlanPostponed
from journal.events.rows.plan_reopened import PlanReopened
from journal.events.rows.plan_finished import PlanFinished
from journal.events.rows.plan_started import PlanStarted
from journal.models.scoped import Scoped
from journal.models.task import Task
from journal.models.phase_states import PhaseStates
from journal.models.support.dock_button import DockButton
from journal.models.support.dock_card import DockCard
from journal.support.rejection import Rejection


@dataclass(frozen=True)
class Plan(Scoped):
    """Ordered work: its phases and tasks are linked to it. Created as draft, marked ready by the agent, in review while reviewers read it, counting those still out, approved by the user, then followed: finishing one task starts the next. A start is refused while it is blocked or unapproved; a done plan given work again is reopened without that check. Its questions about its tasks are answered from the rows its repository gives it: finished when every task is closed, all blocked, the tasks in order phase by phase then the unphased ones, the next open task that can start, the task to resume (its postponed one first), the current phase (the first with open work, else the last) and the checkpoint it is at (a checkpoint phase done, the next phase's work not started). A hub plan names the person and the agent driving it."""

    text_fields: ClassVar[tuple[str, ...]] = ("title", "brief")

    title: str = ""
    brief: str = ""
    state: PlanState = PlanState.DRAFT
    block_reason: str = ""
    reviewers: int = 0
    driver: str = ""
    driver_agent: str = ""

    def waiting_reason(self) -> str:
        return self.block_reason

    def ready(self) -> "Plan":
        return self.moved(PlanState.READY)

    def reviewing(self) -> "Plan":
        return self.moved(PlanState.REVIEWING)

    def reviewers_counted(self, reviewers: int, time: float) -> "Plan":
        counted = self.with_(reviewers=reviewers)
        if self.state != PlanState.REVIEWING or reviewers or not self.reviewers:
            return counted
        return counted.with_event(PlanReviewed(environment_id=self.environment_id, time=time, plan_id=self.row_id))

    def approved(self, time: float, user_origin: bool) -> "Plan":
        return self.moved(PlanState.APPROVED).with_event(PlanApproved(environment_id=self.environment_id, time=time, plan_id=self.row_id, user_origin=user_origin))

    def task_startable(self, task_id: int) -> "Plan":
        if self.state.is_unapproved():
            raise Rejection(f"task {task_id} belongs to plan {self.id}, which is {self.state} and not approved: only the user approves a plan, on its page or with journal plan approve {self.id}, and no instruction stands in for that; until then its tasks are not started or handed to a worker")
        return self

    def startable(self) -> "Plan":
        if self.is_blocked():
            raise Rejection(f"plan {self.id} is blocked, waiting on: {self.block_reason or 'what it was blocked on'}; `journal plan unblock {self.id}` when it may go on")
        if not self.state.is_startable():
            raise Rejection(f"plan {self.id} is {self.state}, not approved: the user approves it first")
        return self

    def started(self, first: Task, time: float) -> "Plan":
        return self.startable().moved(PlanState.STARTED).with_event(PlanStarted(environment_id=self.environment_id, time=time, plan_id=self.row_id, task_id=first.row_id))

    def started_without_task(self, time: float) -> "Plan":
        return self.startable().reopened(time)

    def reopened(self, time: float) -> "Plan":
        return self.moved(PlanState.STARTED).with_event(PlanStarted(environment_id=self.environment_id, time=time, plan_id=self.row_id, task_id=0))

    def postponed(self, time: float, user_origin: bool) -> "Plan":
        return self.moved(PlanState.PAUSED).with_event(PlanPostponed(environment_id=self.environment_id, time=time, plan_id=self.row_id, user_origin=user_origin))

    def blocked(self, reason: str, time: float) -> "Plan":
        return self.moved(PlanState.BLOCKED).with_(block_reason=reason).with_event(PlanBlocked(environment_id=self.environment_id, time=time, plan_id=self.row_id, reason=reason))

    def unblocked(self, reason: str, time: float) -> "Plan":
        return self.moved(PlanState.STARTED).with_(block_reason="").with_event(PlanReopened(environment_id=self.environment_id, time=time, plan_id=self.row_id, reason=reason))

    def is_blocked(self) -> bool:
        return self.state == PlanState.BLOCKED

    def finished(self, time: float) -> "Plan":
        return self.moved(PlanState.FINISHED).with_event(PlanFinished(environment_id=self.environment_id, time=time, plan_id=self.row_id))

    def cancelled(self, time: float, user_origin: bool) -> "Plan":
        return self.moved(PlanState.CANCELLED).with_event(PlanAbandoned(environment_id=self.environment_id, time=time, plan_id=self.row_id, user_origin=user_origin))

    def moved(self, state: PlanState) -> "Plan":
        if not self.state.can_become(state):
            raise Rejection(f"plan {self.id} is {self.state} and cannot become {state}")
        return self.with_(state=state)

    def is_finished(self, task_count: int, remaining_count: int) -> bool:
        return bool(task_count) and not remaining_count

    def is_stalled(self, remaining_count: int, blocked_count: int) -> bool:
        return bool(remaining_count) and remaining_count == blocked_count

    def current_phase(self, phases: list[PhaseStates]) -> int:
        return next((phase.number for phase in phases if phase.has_open_work()), len(phases) or 1)

    def checkpoint_phase(self, phases: list[PhaseStates]) -> PhaseStates | None:
        for previous, following in zip(phases, phases[1:]):
            if previous.phase.checkpoint and previous.is_finished() and following.has_tasks() and not following.has_work_started():
                return previous
        return None

    def ended_phase(self, phases: list[PhaseStates]) -> PhaseStates | None:
        return next((previous for previous, following in zip(phases, phases[1:]) if previous.is_finished() and following.has_tasks() and not following.has_work_started()), None)

    def title_words(self) -> str:
        return self.title

    def summary_line(self) -> str:
        return self.opening_line(self.brief)

    def docked(self) -> DockCard:
        return DockCard((DockButton("Open plan", "open"), DockButton("Approve", "approve"), DockButton("Close", "close")))
