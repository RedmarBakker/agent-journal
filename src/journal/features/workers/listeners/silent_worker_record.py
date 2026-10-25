from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.features.workers.workers_nudges import WorkersNudges


class SilentWorkerRecord(AgentListener[LineDelivered]):
    """A silent worker reported to the agent is marked as reported on its row, and once more when it is still quiet at twice the span with the advice to split its job, so its silence is reported twice at most; its next send, notify or report starts a new span."""

    def __init__(self, workers: Workers) -> None:
        self.workers = workers

    def handle(self, event: LineDelivered) -> None:
        if event.nudge not in (WorkersNudges.SILENT_WORKER.key, WorkersNudges.SPLIT_ADVICE.key):
            return
        worker = self.workers.find(int(event.values["n"]))
        silence = worker.silence.reported() if event.nudge == WorkersNudges.SILENT_WORKER.key else worker.silence.split_advised()
        self.workers.touch(worker, Actor.system(), silence=silence)
