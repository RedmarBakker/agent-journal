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

OPEN_TASK_LIMIT_SECONDS = 900.0
COMPACT = "compact"


@dataclass(frozen=True)
class Working(BaseState):
    """On one task. Writes are counted since the last log line: once N writes or so many minutes have passed since it, whichever is first, the log is asked for on the next tool use, once; every M writes the task is named back, and past the limit the next write waits for the log line. A stop with the task in hand is told to carry on, with the log line first once the same span has passed; a session resumed with it is told where it stands; a quiet quarter hour is told it is still open. Pushed by journal task start, popped by done and park."""

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

    def label(self) -> str:
        if self.task_id and self.focus:
            return f"task {self.task_id}, {self.focus}"
        return f"task {self.task_id}" if self.task_id else f"the work in hand, {self.focus}"

    def logged(self, time: float) -> "Working":
        return replace(self, logged_at=time, edits=0, log_requested=False, reminder_edits=0)

    def log_span(self, settings: Settings) -> Timeout:
        from journal.features.tasks.feature import Tasks
        return Timeout.edits(settings.integer(Tasks.FIRST_DELAY)).combined(Timeout.minutes(settings.integer(Tasks.LOG_AGE_LIMIT))).reset(Moment(seconds=self.logged_at))

    def is_log_due(self, time: float, settings: Settings) -> bool:
        return self.log_span(settings).has_passed(Moment(seconds=time, edits=self.edits))

    def log_command(self) -> str:
        return f"journal task log {self.task_id}" if self.task_id else "journal task log"

    def logged_words(self, time: float) -> str:
        minutes = int((time - self.logged_at) // 60)
        return "last logged just now" if minutes < 1 else f"last logged {minutes} min ago"

    def continue_nudge(self, time: float) -> Nudge:
        from journal.features.tasks.feature import Tasks
        return Tasks.TASK_CONTINUATION.create(name=self.label(), logged=self.logged_words(time))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        from journal.features.tasks.feature import Tasks
        active = replace(self, active_at=event.time)
        if event.subagent:
            return self.swap(active)
        if not event.call.writes:
            return self.log_request(active, event.time, settings)
        if Timeout.edits(settings.integer(Tasks.LOG_LIMIT)).is_elapsed(self.edits):
            return self.refuse(Tasks.LOG_EDIT_BLOCK.create(edits=self.edits, name=self.label(), log=self.log_command()))
        counted = replace(active, edits=self.edits + 1)
        if Timeout.edits(settings.integer(Tasks.TASK_REMINDER_INTERVAL)).started(self.reminder_edits).is_elapsed(self.edits):
            return self.log_request(replace(counted, reminder_edits=self.edits), event.time, settings, Tasks.CURRENT_TASK_REMINDER.create(name=self.label(), edits=self.edits))
        return self.log_request(counted, event.time, settings)

    def log_request(self, working: "Working", time: float, settings: Settings, *lines: Nudge) -> Transition:
        from journal.features.tasks.feature import Tasks
        if self.log_requested or not self.is_log_due(time, settings):
            return self.swap(working, *lines)
        request = Tasks.LOG_REQUEST.create(edits=self.edits, name=self.label(), log=self.log_command())
        return self.swap(replace(working, log_requested=True), request, *lines)

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        from journal.features.tasks.feature import Tasks
        if self.is_log_due(event.time, settings):
            return self.refuse(Tasks.STOP_LOG_REQUEST.create(name=self.label(), logged=self.logged_words(event.time), log_command=self.log_command()))
        return self.refuse(self.continue_nudge(event.time))

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        from journal.features.briefing.feature import Briefing
        from journal.features.git.feature import Git
        from journal.features.tasks.feature import Tasks
        nudges = [self.continue_nudge(event.time)]
        if event.source == COMPACT:
            nudges.append(Briefing.COMPACTION_SUMMARY.create(task=self.label(), last_log=event.data.part(Tasks).last_log_line, uncommitted=event.data.part(Git).uncommitted))
        return self.swap(replace(self, active_at=event.time), *nudges)

    def on_prompt_submitted(self, event: PromptSubmitted, settings: Settings) -> Transition:
        return self.swap(replace(self, active_at=event.time))

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        from journal.features.tasks.feature import Tasks
        if Timeout.seconds(OPEN_TASK_LIMIT_SECONDS).is_elapsed(event.silence_seconds):
            return self.none(Tasks.OPEN_TASK.create(name=self.label()))
        return self.none()

    def on_task_logged(self, event: TaskLogged, settings: Settings) -> Transition:
        return self.swap(self.logged(event.time)) if event.task_id == self.task_id else self.none()

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        return self.pop() if event.task_id == self.task_id else self.none()

    def on_resume(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...] | Transition:
        from journal.features.tasks.feature import Tasks
        if self.task_id and data.part(Tasks).current_task != self.task_id:
            return self.pop()
        return ()
