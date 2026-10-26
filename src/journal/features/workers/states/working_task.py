from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.command_ended import CommandEnded
from journal.events.agent.impasse_report import ImpasseReport
from journal.events.agent.wait_request import WaitRequest
from journal.events.agent.stop import Stop
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.events.rows.worker_review_requested import WorkerReviewRequested
from journal.features.shell.support.activity_label import ActivityLabel
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.impasse import Impasse
from journal.features.tasks.tasks_part import TasksPart
from journal.features.workers.listeners.worker_task_changes import RELEASING
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import JOURNAL_TESTING, MERGER_TESTING, TEST_BUDGET, WorkersOptions
from journal.features.workers.workers_part import WorkersPart

TESTING_REFUSALS = {MERGER_TESTING: WorkersNudges.TEST_HANDOVER, TEST_BUDGET: WorkersNudges.TEST_BUDGET_REFUSAL, JOURNAL_TESTING: WorkersNudges.JOURNAL_TESTS_REFUSAL}


@dataclass(frozen=True)
class WorkingTask(BaseState):
    """A worker at work on its task, pushed over Void when it clocks in and popped back to Void when its work is delivered, sent to review, or its task is closed by the user: its writes wait while the journal rebases its worktree, it never runs git, it runs tests only as the setting says, its stop waits for an output of its own still running and is told the to-do items still open, it is told the end of each of its outputs, its journal await and journal stuck push the wait and the stuck state over its work."""

    name = "working_task"
    title = "At work on its task"
    task_id: int = 0

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        rows = event.data.part(WorkersPart).session_workers
        if event.call.writes and rows and rows[0].edit_lock:
            return self.refuse(WorkersNudges.EDIT_LOCK.create())
        if any(part.is_git for part in event.call.parts):
            return self.refuse(WorkersNudges.WORKER_GIT_REFUSAL.create())
        tests = ActivityLabel.test_runs(tuple(part.text for part in event.call.parts))
        refusal = TESTING_REFUSALS.get(str(settings.value(WorkersOptions.TESTING)))
        return self.refuse(refusal.create(command=tests[0])) if tests and refusal else self.none()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        unfinished = event.data.part(WorkersPart).unfinished_outputs
        if unfinished:
            return self.refuse(WorkersNudges.OUTPUT_UNFINISHED.create(n=unfinished[0]))
        items = [item for item in event.data.part(WorkersPart).todos if not item.complete]
        return self.none(WorkersNudges.OPEN_TODOS.create(count=len(items), items="; ".join(f"{item.position}. {item.text}" for item in items))) if items else self.none()

    def on_command_ended(self, event: CommandEnded, settings: Settings) -> Transition:
        return self.none(WorkersNudges.OUTPUT_END.create(n=event.output, status=event.status))

    def on_wait_request(self, event: WaitRequest, settings: Settings) -> Transition:
        return self.push(ExternalWait.opened(*event.wait_terms()))

    def on_impasse_report(self, event: ImpasseReport, settings: Settings) -> Transition:
        return self.push(Impasse(reason=event.reason))

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        if event.task_id not in event.data.part(TasksPart).agent_tasks or event.outcome not in RELEASING:
            return self.none()
        return self.pop(WorkersNudges.USER_CLOSURE.create(task=event.task_id))

    def on_worker_delivered(self, event: WorkerDelivered, settings: Settings) -> Transition:
        return self.pop() if is_mine(event) else self.none()

    def on_worker_review_requested(self, event: WorkerReviewRequested, settings: Settings) -> Transition:
        return self.pop() if is_mine(event) else self.none()


def is_mine(event: WorkerDelivered | WorkerReviewRequested) -> bool:
    return event.worker.id in {worker.id for worker in event.data.part(WorkersPart).session_workers}
