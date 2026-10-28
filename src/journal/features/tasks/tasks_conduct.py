import re
import shlex
from journal.events.rows.task_wait_ended import TaskWaitEnded
from journal.features.tasks.support.task_succession import TaskSuccession
from journal.engine.conduct import Conduct
from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.wait_request import WaitRequest
from journal.events.agent.impasse_report import ImpasseReport
from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent.ticked import Ticked
from journal.events.agent.stop import Stop
from journal.events.rows.row_resolved import RowResolved
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_arrived import TaskArrived
from journal.events.rows.task_reopened import TaskReopened
from journal.events.rows.task_test_failed import TaskTestFailed
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.tasks.tasks_part import TasksPart
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.impasse import Impasse
from journal.features.tasks.support.wait_estimate import WaitEstimate
from journal.models.check import Check
from journal.models.command_output import CommandOutput
from journal.support.timespan import Timespan

POLL_REPEAT_COMMANDS = 3
WAITED_OUTPUT = re.compile(r"--output[ =](\d+)")
WAIT_REASON = re.compile(r"--why[ =](?:\"([^\"]*)\"|'([^']*)'|(\S+))")
POLLED_OUTPUT = re.compile(r"^journal output (?:status|read) (\d+)(?: --tail \d+)?$")
AWAIT_REFUSAL_COUNT = 2


class TasksConduct(Conduct):
    """The tasks feature's conduct in every state: a polled command named, a task open again informed, a task whose test run failed named to its agent, a test run started while the task in hand has been in progress a while met with how to put it in testing, a paused task named when a task closes, unless the choice of paused work will ask at the stop, a wait the agent declares pushed as Expecting and a stuck agent pushed as Stuck."""

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        return wake_check(self, event, settings)

    def on_wait_request(self, event: WaitRequest, settings: Settings) -> Transition:
        return self.push(ExternalWait.opened_beside(event.data, *event.wait_terms()))

    def on_impasse_report(self, event: ImpasseReport, settings: Settings) -> Transition:
        return self.push(Impasse(reason=event.reason))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return Transition.merged(self, [polling_check(self, event), output_poll_check(self, event), impasse_check(self, event), priorities_check(self, event, settings), wait_check(self, event, settings), testing_suggestion(self, event, settings)])

    def on_row_resolved(self, event: RowResolved, settings: Settings) -> Transition:
        passed = [wait for wait in event.data.part(TasksPart).passed_waits if f"{Check.table()}:{wait.check_id}" == event.ref]
        return self.none(*(TasksNudges.WAIT_CHECK_PASSED.create(what=wait.purpose, lines=wait.lines) for wait in passed))

    def on_task_reopened(self, event: TaskReopened, settings: Settings) -> Transition:
        return self.none(TasksNudges.TASK_REOPENED.create(n=event.task_id, reason=event.reason))

    def on_task_wait_ended(self, event: TaskWaitEnded, settings: Settings) -> Transition:
        return self.none(TasksNudges.PAUSE_WAIT_END.create(n=event.task_id, reason=event.reason))

    def on_task_test_failed(self, event: TaskTestFailed, settings: Settings) -> Transition:
        if event.task_id not in event.data.part(TasksPart).agent_tasks:
            return self.none()
        return self.none(TasksNudges.TEST_FAILURE.create(n=event.task_id, output=event.output_id, outcome=event.outcome))

    def on_task_arrived(self, event: TaskArrived, settings: Settings) -> Transition:
        return self.none(TasksNudges.TASK_ARRIVED.create(n=event.task_id, source=event.source, state=event.state))

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        tasks = event.data.part(TasksPart)
        if event.outcome != "completed" or tasks.current_task or not tasks.paused or tasks.choosable or event.data.part(TaskSuccession):
            return self.none()
        return self.none(TasksNudges.PAUSED_TASK_CLOSURE_REMINDER.create(n=tasks.paused[0], why=tasks.first_pause_reason))


def testing_suggestion(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    task = event.data.part(TasksPart).current_task_row
    if task is None or not task.is_started() or not event.call.test_runs():
        return state.none()
    limit = Timespan(tool_uses=settings.integer(TasksOptions.TESTING_SUGGESTION_TOOL_USES), seconds=settings.integer(TasksOptions.TESTING_SUGGESTION_MINUTES) * 60)
    return state.none(TasksNudges.TESTING_SUGGESTION.create(n=task.row_id)) if limit <= task.progress_span(event.time) else state.none()


def priorities_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    unset = event.data.part(TasksPart).unprioritised
    if len(unset) < settings.integer(TasksOptions.PRIORITY_REMIND_TASKS):
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


def wait_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    if not event.call.is_journal_noun("await"):
        return state.none()
    tasks, work = event.data.part(TasksPart), event.data.next_work()
    if work is None:
        return state.none()
    wait_line = event.call.journal_text("await")
    if WAITED_OUTPUT.findall(wait_line):
        return state.none()
    estimate = WaitEstimate.create([f"{CommandOutput.table()}:{n}" for n in WAITED_OUTPUT.findall(wait_line)], tasks.wait_progress, event.time)
    if estimate.is_short(settings):
        return state.none()
    arguments = shlex.split(wait_line)
    wait_name = arguments[2] if len(arguments) > 2 else "the process"
    if await_count(tasks.command_lines[:-1]) >= AWAIT_REFUSAL_COUNT:
        return reasoned_wait(state, wait_line, wait_name, estimate.seconds_text())
    if tasks.current_task:
        return state.refuse(TasksNudges.WAIT_SWITCH_REFUSAL.create(what=wait_name, left=estimate.seconds_text(), n=work.id))
    return state.refuse(TasksNudges.WAIT_REFUSAL.create(what=wait_name, left=estimate.seconds_text(), n=work.id))


def await_count(commands: tuple[str, ...]) -> int:
    return sum(1 for command in commands if command.startswith("journal await "))


def reasoned_wait(state: BaseState, wait_line: str, wait_name: str, remaining_text: str) -> Transition:
    reason_match = WAIT_REASON.search(wait_line)
    if reason_match is None:
        return state.refuse(TasksNudges.WAIT_REASON_REQUEST.create(what=wait_name, left=remaining_text))
    return state.none(TasksNudges.WAIT_REASON_LINE.create(why=next(group for group in reason_match.groups() if group is not None)))


def output_poll_check(state: BaseState, event: ToolStarting) -> Transition:
    polled = POLLED_OUTPUT.match(event.call.command.strip())
    if polled is None:
        return state.none()
    polled_numbers = [line_match.group(1) for command in event.data.part(TasksPart).command_lines[-3:-1] if (line_match := POLLED_OUTPUT.match(command.strip()))]
    return state.refuse(TasksNudges.OUTPUT_POLL_REFUSAL.create(n=polled.group(1))) if polled_numbers == [polled.group(1)] * 2 else state.none()


def impasse_check(state: BaseState, event: ToolStarting) -> Transition:
    if not any(part.text.split()[:2] == ["journal", "stuck"] for part in event.call.parts):
        return state.none()
    tasks = event.data.part(TasksPart)
    work_count = tasks.open_count + len(tasks.started_ids) + len(tasks.paused)
    if not work_count:
        return state.none()
    return state.refuse(TasksNudges.IMPASSE_REFUSAL.create(count=work_count))


def wake_check(state: BaseState, event: Ticked, settings: Settings) -> Transition:
    tasks = event.data.part(TasksPart)
    minutes = settings.integer(TasksOptions.WAKE_MINUTES)
    if not minutes or not tasks.turn_finished or tasks.wake_count >= settings.integer(TasksOptions.WAKE_COUNT):
        return state.none()
    if event.silence_seconds < minutes * 60:
        return state.none()
    return state.follow(Stop(session=event.session, environment_id=event.environment_id, prior_refusal=False, time=event.time), TasksNudges.STOPPED_WITH_WORK.create())
