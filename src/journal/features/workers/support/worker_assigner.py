from journal.engine.command_events import CommandEvents
from journal.events.agent.helper_assignment import HelperAssignment
from journal.features.workers.states.working_task import WorkingTask
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.agents import Agents
from journal.repositories.tasks import Tasks


class WorkerAssigner:
    """Puts a clocked-in worker to work on the task it holds, once its session has an agent row: Void, the helper's floor, hears the assignment and pushes WorkingTask over itself; a pool worker on the machine that runs it is put to work at its clock-in, since its clock-in is made on the journal that dispatched it."""

    def __init__(self, tasks: Tasks, agents: Agents, events: CommandEvents) -> None:
        self.tasks, self.agents, self.events = tasks, agents, events

    def assigned(self, row: Worker) -> None:
        if row.state == WorkerState.READY:
            self.assign(row)

    def assign(self, row: Worker) -> None:
        task_ids = self.tasks.holder_task_ids(Ref.build(row))
        if task_ids and self.has_agent(row):
            self.events.helper_assigned(HelperAssignment(state=WorkingTask(task_id=task_ids[0])), row.session, row.provider)

    def has_agent(self, row: Worker) -> bool:
        return bool(row.session) and bool(self.agents.session_rows(row.session))
