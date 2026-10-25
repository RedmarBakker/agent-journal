from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.command_ended import CommandEnded
from journal.events.agent.stop import Stop
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.events.rows.worker_ready import WorkerReady
from journal.events.rows.worker_review_requested import WorkerReviewRequested
from journal.features.tasks.states.working import Working
from journal.features.workers.listeners.worker_task_changes import RELEASING
from journal.models.worker_state import WorkerState
from journal.features.tasks.tasks_part import TasksPart
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_part import WorkersPart
from journal.features.workers.workers_options import MERGER_TESTING, TEST_BUDGET, WorkersOptions
from journal.features.shell.support.activity_label import TESTING, ActivityLabel


class ClockConduct(Conduct):
    """A worker's own conduct in every state: its writes wait until it clocks in, with that as the only message; clocking in puts it to work on the task it owns, a stop is blocked while an output of its own runs and the worker is informed the end of one that ended, and informed the to-do items still open, the user closing its task ends its work and the user rewriting its brief names the points to prove again, and clocking out ends that work, so it may stop, whether its work goes to the agent or to the journal's reviewer."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        rows = event.data.part(WorkersPart).session_workers
        if event.call.writes and rows and rows[0].state == WorkerState.DISPATCHED:
            return self.refuse(WorkersNudges.READINESS.create())
        tests = [part.text for part in event.call.parts if ActivityLabel.build(part.text) == TESTING]
        if rows and tests and settings.value(WorkersOptions.TESTING) == MERGER_TESTING:
            return self.refuse(WorkersNudges.TEST_HANDOVER.create(command=tests[0]))
        if rows and tests and settings.value(WorkersOptions.TESTING) == TEST_BUDGET:
            return self.refuse(WorkersNudges.TEST_BUDGET_REFUSAL.create(command=tests[0]))
        return self.none()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        unfinished = event.data.part(WorkersPart).unfinished_outputs
        if unfinished:
            return self.refuse(WorkersNudges.OUTPUT_UNFINISHED.create(n=unfinished[0]))
        items = [item for item in event.data.part(WorkersPart).todos if not item.complete]
        return self.none(WorkersNudges.OPEN_TODOS.create(count=len(items), items="; ".join(f"{item.position}. {item.text}" for item in items))) if items else self.none()

    def on_command_ended(self, event: CommandEnded, settings: Settings) -> Transition:
        return self.none(WorkersNudges.OUTPUT_END.create(n=event.output, status=event.status))

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        if event.task_id not in event.data.part(TasksPart).agent_tasks or event.outcome not in RELEASING:
            return self.none()
        return self.pop(WorkersNudges.USER_CLOSURE.create(task=event.task_id))

    def on_worker_ready(self, event: WorkerReady, settings: Settings) -> Transition:
        holdings = event.data.part(TasksPart).agent_tasks
        return self.push(Working(task_id=holdings[0], logged_at=event.time)) if holdings else self.none()

    def on_worker_delivered(self, event: WorkerDelivered, settings: Settings) -> Transition:
        return self.pop()

    def on_worker_review_requested(self, event: WorkerReviewRequested, settings: Settings) -> Transition:
        return self.pop()
