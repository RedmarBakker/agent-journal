from collections.abc import Mapping
from dataclasses import dataclass, replace

from journal.engine.nudge import Nudge
from journal.engine.states.wait import Wait
from journal.events.agent.wait_cleared import WaitCleared
from journal.events.agent.wait_request import WaitRequest
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.ticked import Ticked
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.row_pending import RowPending
from journal.events.rows.row_resolved import RowResolved
from journal.events.rows.task_started import TaskStarted
from journal.support.permission import Permission
from journal.support.timeout import Timeout
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.tasks.tasks_part import TasksPart
from journal.features.tasks.support.wait_estimate import WaitEstimate
from journal.features.tasks.support.wait_progress import WaitProgress
from journal.events.feature_data import FeatureData
from journal.models.check import Check
from journal.models.command_output import CommandOutput

NEXT_TASK_DELAY = Timeout.minutes(1)
CHECK_REMINDER = Timeout.minutes(5)
PRINTING_REMINDER = Timeout.minutes(15)


@dataclass(frozen=True)
class ExternalWait(Wait):
    """The agent waits for something outside its control, named in words and by the rows that end it, table:id each: outputs, checks, tasks or questions, and whatever a feature above tasks adds. Each row resolving is reported and the last pops the wait with the result of each. The wait ends when the agent uses any tool outside the journal. A stop while a task is open is refused in auto mode, as it is with no wait, unless the wait is estimated short; a run it waits on with progress to read is estimated at the first tick that can: a short wait is waited out, a long one is parked, the wait ending, and the agent carries on with the next task; with nothing to estimate by, in auto mode the next task is named once after a minute, and every five idle minutes the agent is asked to check, every fifteen while a run it waits on printed within the last five."""

    name = "awaiting"
    assigner = None
    title = "Waiting"
    allows = frozenset({Permission.FILE_EDITS, Permission.RUN_COMMANDS, Permission.DISPATCH_SUBAGENTS})
    focus: str = ""
    end_refs: str = ""
    started_at: float = 0.0
    next_task_delay: Timeout = NEXT_TASK_DELAY
    check_reminder: Timeout = CHECK_REMINDER
    next_task_reported: bool = False
    decided: bool = False
    started_task: int = 0
    started_title: str = ""
    outcomes: str = ""

    @classmethod
    def opened(cls, focus: str, end_refs: str, started_at: float) -> "ExternalWait":
        return cls(focus=focus, end_refs=end_refs, started_at=started_at, next_task_delay=NEXT_TASK_DELAY.started(started_at), check_reminder=CHECK_REMINDER.started(started_at))

    def wait_description(self) -> tuple[str, str]:
        return self.focus, self.end_refs

    def is_output_wait(self) -> bool:
        return any(target.startswith(f"{CommandOutput.table()}:") for target in self.targets())

    def targets(self) -> list[str]:
        return [ref for ref in self.end_refs.split(",") if ref]

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if event.call.is_journal:
            return self.none()
        return self.pop(*self.lifted_lines(event.data))

    def lifted_lines(self, data: FeatureData) -> tuple[Nudge, ...]:
        prefix = f"{Check.table()}:"
        numbers = [int(ref.removeprefix(prefix)) for ref in self.targets() if ref.startswith(prefix)]
        polled = data.part(TasksPart).polled_checks if numbers else ()
        return tuple(TasksNudges.WAIT_LIFTED.create(what=self.focus, n=number) for number in numbers if number in polled)

    def on_wait_cleared(self, event: WaitCleared, settings: Settings) -> Transition:
        return self.pop()

    def remaining_seconds(self, progress: Mapping[str, WaitProgress], moment: float) -> float | None:
        estimates = [seconds for ref in self.targets() if ref in progress and (seconds := progress[ref].remaining_seconds(moment)) is not None]
        return max(estimates) if estimates else None

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        return self.swap(replace(self, started_task=event.task_id, started_title=event.title))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        if self.started_task:
            return Transition.merged(self, [self.swap(replace(self, started_task=0, started_title="")), self.refuse(TasksNudges.WAIT_NEXT_TASK.create(what=self.focus, n=self.started_task, title=self.started_title))])
        tasks = event.data.part(TasksPart)
        estimate = WaitEstimate.create(self.targets(), tasks.wait_progress, event.time)
        work = event.data.next_work()
        if self.is_output_wait() or work is None or estimate.is_short(settings):
            return self.none()
        return self.refuse(TasksNudges.WAIT_STOP.create(what=self.focus, left=estimate.seconds_text(), n=work.id))

    def estimated(self, remaining: float, data: FeatureData, settings: Settings) -> Transition:
        work = data.next_work()
        seconds = round(remaining)
        if self.is_output_wait() or remaining <= settings.integer(TasksOptions.SHORT_WAIT_SECONDS) or work is None:
            return self.swap(replace(self, decided=True), TasksNudges.WAIT_SHORT.create(what=self.focus, seconds=seconds))
        return self.pop(TasksNudges.WAIT_LONG.create(what=self.focus, seconds=seconds, n=work.id), *self.lifted_lines(data))

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        tasks = event.data.part(TasksPart)
        remaining = self.remaining_seconds(tasks.wait_progress, event.time)
        if remaining is not None and not self.decided:
            return self.estimated(remaining, event.data, settings)
        work_lines = self.next_work_lines(event.data)
        if not self.next_task_reported and self.next_task_delay.is_elapsed(event.time) and work_lines:
            return self.swap(replace(self, next_task_reported=True), *work_lines)
        if self.reminder(tasks.wait_progress, event.time).is_elapsed(event.time):
            return self.swap(replace(self, check_reminder=self.check_reminder.started(event.time)), TasksNudges.WAIT_CHECK.create(what=self.focus, minutes=int((event.time - self.started_at) // 60)))
        return self.none()

    def next_work_lines(self, data: FeatureData) -> tuple[Nudge, ...]:
        tasks, work = data.part(TasksPart), data.next_work()
        if work is not None:
            return (TasksNudges.WAIT_NEXT_TASK.create(what=self.focus, n=work.id, title=work.title),)
        if tasks.paused:
            return (TasksNudges.WAIT_PAUSED_TASK.create(what=self.focus, n=tasks.paused[0], why=tasks.first_pause_reason),)
        return ()

    def reminder(self, progress: Mapping[str, WaitProgress], moment: float) -> Timeout:
        printing = any(progress[ref].output_time >= moment - CHECK_REMINDER.amount for ref in self.targets() if ref in progress)
        return (PRINTING_REMINDER if printing else CHECK_REMINDER).started(self.check_reminder.start)

    def on_row_resolved(self, event: RowResolved, settings: Settings) -> Transition:
        return self.resolution(event.ref, event.outcome)

    def on_row_pending(self, event: RowPending, settings: Settings) -> Transition:
        if event.awaiter != event.session:
            return self.none()
        event.stop_propagation()
        if event.ref in self.targets():
            return self.none()
        return self.swap(replace(self, focus=f"{self.focus}, {event.label}", end_refs=",".join([*self.targets(), event.ref])))

    def on_wait_request(self, event: WaitRequest, settings: Settings) -> Transition:
        event.stop_propagation()
        added = [ref for ref in event.end_refs.split(",") if ref and ref not in self.targets()]
        if not added:
            return self.none()
        return self.swap(replace(self, focus=f"{self.focus}, {event.focus}", end_refs=",".join([*self.targets(), *added])))

    def resolution(self, ref: str, outcome: str, *lines: Nudge) -> Transition:
        if ref not in self.targets():
            return self.none()
        remaining = [waited for waited in self.targets() if waited != ref]
        outcomes = "; ".join(part for part in (self.outcomes, outcome) if part)
        if remaining:
            return self.swap(replace(self, end_refs=",".join(remaining), outcomes=outcomes), *lines)
        return self.pop(*lines, TasksNudges.WAIT_END.create(what=self.focus, outcome=outcomes))
