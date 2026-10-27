from journal.engine.base_state import BaseState
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.features.workers.support.worker_line import WorkerLine
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_part import WorkersPart

# what the line calls a worker a dispatch has not numbered yet
NEW_WORKER = ("a new worker", "<its number>")


def queue_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    lines = [line for part in event.call.parts if (line := WorkerLine.parsed(part.text)) and line.verb in ("dispatch", "send") and line.task]
    return state.none(*(nudge for line in lines for nudge in queue_lines(event, line)))


def queue_lines(event: ToolStarting, line: WorkerLine) -> tuple[Nudge, ...]:
    workers = event.data.part(WorkersPart)
    queued = {task for queue in workers.queues.values() for task in queue}
    plan_mates = {task for plan in workers.plan_tasks if line.task in plan for task in plan}
    related = [task for task in workers.delegable if task in plan_mates and task != line.task and task not in queued]
    if not related:
        return ()
    worker, n = NEW_WORKER if line.verb == "dispatch" else (f"worker {line.number}", line.number)
    return (WorkersNudges.QUEUE_RELATED.create(task=line.task, worker=worker, n=n, listed=", ".join(map(str, related)), tasks=" ".join(map(str, related))),)
