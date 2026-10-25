from journal.events.rows.task_wait_ended import TaskWaitEnded
from journal.features.tasks.support.task_succession import TaskSuccession
from journal.engine.conduct import Conduct
from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.wait_request import WaitRequest
from journal.events.agent.impasse_report import ImpasseReport
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_reopened import TaskReopened
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.tasks.tasks_part import TasksPart
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.impasse import Impasse

POLL_REPEAT_COMMANDS = 3


class TasksConduct(Conduct):
    """The tasks feature's conduct in every state: a polled command named, a task open again informed, a paused task named when a task closes, a wait the agent declares pushed as Expecting and a stuck agent pushed as Stuck."""

    def on_wait_request(self, event: WaitRequest, settings: Settings) -> Transition:
        return self.push(ExternalWait.opened(*event.wait_terms()))

    def on_impasse_report(self, event: ImpasseReport, settings: Settings) -> Transition:
        return self.push(Impasse(reason=event.reason))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return Transition.merged(self, [polling_check(self, event), impasse_check(self, event), priorities_check(self, event, settings)])

    def on_task_reopened(self, event: TaskReopened, settings: Settings) -> Transition:
        return self.none(TasksNudges.TASK_REOPENED.create(n=event.task_id, reason=event.reason))

    def on_task_wait_ended(self, event: TaskWaitEnded, settings: Settings) -> Transition:
        return self.none(TasksNudges.PAUSE_WAIT_END.create(n=event.task_id, reason=event.reason))

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        tasks = event.data.part(TasksPart)
        if event.outcome != "completed" or tasks.current_task or not tasks.paused or event.data.part(TaskSuccession):
            return self.none()
        return self.none(TasksNudges.PAUSED_TASK_CLOSURE_REMINDER.create(n=tasks.paused[0], why=tasks.first_pause_reason))


def priorities_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    unset = event.data.part(TasksPart).unprioritised
    if event.subagent or len(unset) < settings.integer(TasksOptions.PRIORITY_REMIND_TASKS):
        return state.none()
    return state.none(TasksNudges.PRIORITIES_REMINDER.create(count=len(unset), tasks=", ".join(str(task) for task in unset)))


def polling_check(state: BaseState, event: ToolStarting) -> Transition:
    command = event.call.command
    if not command:
        return state.none()
    last = event.data.part(TasksPart).last_commands
    if len(last) < POLL_REPEAT_COMMANDS or any(older != command for older in last):
        return state.none()
    return state.none(TasksNudges.STOP_POLLING.create(times=POLL_REPEAT_COMMANDS, command=command))


def impasse_check(state: BaseState, event: ToolStarting) -> Transition:
    if not any(part.text.split()[:2] == ["journal", "stuck"] for part in event.call.parts):
        return state.none()
    tasks = event.data.part(TasksPart)
    work_count = tasks.open_count + len(tasks.started_ids) + len(tasks.paused)
    if not work_count:
        return state.none()
    return state.refuse(TasksNudges.IMPASSE_REFUSAL.create(count=work_count))
