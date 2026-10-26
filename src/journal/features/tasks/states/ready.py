from dataclasses import dataclass, replace
from typing import Self

from journal.features.tasks.support.default_task_assigner import DefaultTaskAssigner
from journal.engine.base_state import BaseState
from journal.support.timeout import Timeout
from journal.support.permission import Permission
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.task_opened import TaskOpened
from journal.events.agent.stop import Stop
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.ticked import Ticked
from journal.events.agent.tool_starting import ToolStarting
from journal.events.feature_data import FeatureData
from journal.events.rows.task_started import TaskStarted
from journal.engine.nudge import Nudge
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_part import TasksPart
from journal.features.tasks.states.choosing_paused_work import ChoosingPausedWork
from journal.features.tasks.states.working import Working

PAUSED_REMINDER_DELAY_SECONDS = 60.0
BLOCKED_REMINDER_DELAY_SECONDS = 45 * 60.0
IDLE_CHECK_DELAY_SECONDS = 30 * 60.0


@dataclass(frozen=True)
class Ready(BaseState):
    """Nothing in hand: the bottom of the stack, never popped. A stop with paused work the agent may choose beside an open task, in auto mode, pushes the choice of paused work; otherwise a stop here is held by a paused task and by a blocked task whose check cannot run; an open task is the assigner's to start before the stack answers. A task this agent holds, once started, pushes Working; one another agent holds does not. The quiet is measured from the agent's last doing. A feature above tasks extends it under the same name, and work modes are states that extend it in turn."""

    name = "idle"
    assigner = DefaultTaskAssigner
    title = "Idle"
    allows = frozenset({Permission.RUN_COMMANDS})
    silenced_at: float = 0.0
    pause_reported: bool = False
    stop_round: int = 0

    def has_silence(self, seconds: float, time: float) -> bool:
        return Timeout.seconds(seconds).started(self.silenced_at).is_elapsed(time)

    def active(self, time: float) -> Self:
        return replace(self, silenced_at=time, pause_reported=False)

    def working_state(self, **fields) -> BaseState:
        return Working(**fields)

    def choice_state(self) -> BaseState | None:
        return ChoosingPausedWork(refusals=1)

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        return self.swap(self.active(event.time))

    @staticmethod
    def task_noun(data: FeatureData, environment_id: int) -> str:
        return data.part(TasksPart).task_nouns.get(environment_id, "task")

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        if event.task_id not in event.data.part(TasksPart).agent_tasks:
            return self.none()
        return self.push(self.working_state(task_id=event.task_id, logged_at=event.time, task_noun=self.task_noun(event.data, event.environment_id)))

    def on_prompt_submitted(self, event: PromptSubmitted, settings: Settings) -> Transition:
        return self.swap(replace(self.active(event.time), stop_round=0))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        active = self.active(event.time)
        return self.swap(active if event.call.is_journal else replace(active, stop_round=0))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        tasks = event.data.part(TasksPart)
        choice = self.choice_state()
        if choice is not None and tasks.choosable and tasks.free_open and not tasks.paused_declined and not event.prior_refusal:
            return Transition.merged(self, [self.push(choice), self.refuse(ChoosingPausedWork.choice_line(tasks))])
        stop_nudges = self.stop_lines(event.data, settings)
        if self.stop_round < len(stop_nudges):
            return Transition.merged(self, [self.swap(replace(self, stop_round=self.stop_round + 1)), self.refuse(stop_nudges[self.stop_round])])
        return self.none()

    def stop_lines(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        tasks = data.part(TasksPart)
        pause_lines = (TasksNudges.PAUSED_TASKS.create(tasks=tasks.pause_summary),) if tasks.paused else ()
        wait_lines = (TasksNudges.BROKEN_WAIT.create(waits=tasks.broken_waits_summary),) if tasks.broken_waits else ()
        return (*pause_lines, *wait_lines, *self.open_lines(data, settings))

    def open_lines(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        return ()

    def silent_nudges(self, data: FeatureData) -> tuple[Nudge, ...]:
        tasks = data.part(TasksPart)
        return (TasksNudges.IDLE_CHECK.create(),) if tasks.next_open or tasks.paused else ()

    def on_task_opened(self, event: TaskOpened, settings: Settings) -> Transition:
        return self.none(TasksNudges.TASK_OPENED.create(n=event.row_id, title=event.title)) if event.is_users() else self.none()

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        tasks = event.data.part(TasksPart)
        if tasks.paused and self.has_silence(PAUSED_REMINDER_DELAY_SECONDS, event.time) and not self.pause_reported:
            return self.swap(replace(self, pause_reported=True), TasksNudges.PAUSED_TASK_REMINDER.create(n=tasks.paused[0], why=tasks.first_pause_reason))
        if tasks.blocked_without_wait and self.has_silence(BLOCKED_REMINDER_DELAY_SECONDS, event.time):
            return self.none(TasksNudges.BLOCKED_TASK_REMINDER.create(tasks=tasks.blocked_without_wait_summary))
        if self.has_silence(IDLE_CHECK_DELAY_SECONDS, event.time):
            return self.none(*self.silent_nudges(event.data))
        return self.none()

