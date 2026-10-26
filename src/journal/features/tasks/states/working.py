from dataclasses import dataclass, replace

from journal.engine.base_state import BaseState
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.ticked import Ticked
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_logged import TaskLogged
from journal.events.feature_data import FeatureData
from journal.support.permission import Permission
from journal.support.moment import Moment
from journal.support.timeout import Timeout
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.tasks.tasks_part import TasksPart
from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.git.feature import Git

OPEN_TASK_LIMIT_SECONDS = 900.0
COMPACT = "compact"


@dataclass(frozen=True)
class Working(BaseState):
    """On one task, named with its team when it is a hub task. Writes are counted since the last log line: once N writes or so many minutes have passed since it, whichever is first, the log is asked for on the next tool use, once; every M writes the task is named back, and past the limit the next write waits for the log line. A stop with the task in hand is instructed to carry on, with the log line first once the same span has passed; a session resumed with it is informed where it stands; a quiet quarter hour is informed it is still open. Pushed by journal task start, popped by done and pause."""

    name = "working"
    title = "Working"
    allows = frozenset({Permission.FILE_EDITS, Permission.RUN_COMMANDS, Permission.DISPATCH_SUBAGENTS})
    task_id: int = 0
    focus: str = ""
    logged_at: float = 0.0
    edits: int = 0
    active_at: float = 0.0
    log_requested: bool = False
    reminder_edits: int = 0
    task_noun: str = "task"

    def label(self) -> str:
        if self.task_id and self.focus:
            return f"{self.task_noun} {self.task_id}, {self.focus}"
        return f"{self.task_noun} {self.task_id}" if self.task_id else f"the work in hand, {self.focus}"

    def logged(self, time: float) -> "Working":
        return replace(self, logged_at=time, edits=0, log_requested=False, reminder_edits=0)

    def log_span(self, settings: Settings) -> Timeout:
        return Timeout.edits(settings.integer(TasksOptions.FIRST_DELAY)).combined(Timeout.minutes(settings.integer(TasksOptions.LOG_AGE_LIMIT))).reset(Moment(seconds=self.logged_at))

    def is_log_due(self, time: float, settings: Settings) -> bool:
        return self.log_span(settings).has_passed(Moment(seconds=time, edits=self.edits))

    def log_command(self) -> str:
        return f"journal task log {self.task_id}" if self.task_id else "journal task log"

    def logged_words(self, time: float) -> str:
        minutes = int((time - self.logged_at) // 60)
        return "last logged just now" if minutes < 1 else f"last logged {minutes} min ago"

    def continue_nudge(self, time: float) -> Nudge:
        return TasksNudges.TASK_CONTINUATION.create(name=self.label(), logged=self.logged_words(time))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        active = replace(self, active_at=event.time)
        if not event.call.writes:
            return self.log_request(active, event.time, settings)
        if Timeout.edits(settings.integer(TasksOptions.LOG_LIMIT)).is_elapsed(self.edits):
            return self.refuse(TasksNudges.LOG_EDIT_BLOCK.create(edits=self.edits, name=self.label(), log=self.log_command()))
        counted = replace(active, edits=self.edits + 1)
        if Timeout.edits(settings.integer(TasksOptions.TASK_REMINDER_INTERVAL)).started(self.reminder_edits).is_elapsed(self.edits):
            return self.log_request(replace(counted, reminder_edits=self.edits), event.time, settings, TasksNudges.CURRENT_TASK_REMINDER.create(name=self.label(), edits=self.edits))
        return self.log_request(counted, event.time, settings)

    def log_request(self, working: "Working", time: float, settings: Settings, *lines: Nudge) -> Transition:
        if self.log_requested or not self.is_log_due(time, settings):
            return self.swap(working, *lines)
        request = TasksNudges.LOG_REQUEST.create(edits=self.edits, name=self.label(), log=self.log_command())
        return self.swap(replace(working, log_requested=True), request, *lines)

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        if self.is_log_due(event.time, settings):
            return self.refuse(TasksNudges.STOP_LOG_REQUEST.create(name=self.label(), logged=self.logged_words(event.time), log_command=self.log_command()))
        return self.refuse(self.continue_nudge(event.time))

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        nudges = [self.continue_nudge(event.time)]
        if event.source == COMPACT:
            nudges.append(BriefingNudges.COMPACTION_SUMMARY.create(task=self.label(), last_log=event.data.part(TasksPart).last_log_line, uncommitted=event.data.part(Git).uncommitted))
        return self.swap(replace(self, active_at=event.time), *nudges)

    def on_prompt_submitted(self, event: PromptSubmitted, settings: Settings) -> Transition:
        return self.swap(replace(self, active_at=event.time))

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        if Timeout.seconds(OPEN_TASK_LIMIT_SECONDS).is_elapsed(event.silence_seconds):
            return self.none(TasksNudges.OPEN_TASK.create(name=self.label()))
        return self.none()

    def on_task_logged(self, event: TaskLogged, settings: Settings) -> Transition:
        return self.swap(self.logged(event.time)) if event.task_id == self.task_id else self.none()

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        return self.pop() if event.task_id == self.task_id else self.none()

    def on_resume(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...] | Transition:
        if self.task_id and data.part(TasksPart).current_task != self.task_id:
            return self.pop()
        return ()
