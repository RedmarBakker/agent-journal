from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.features.workers.workers_nudges import WorkersNudges


class SilentWorkerRecord(AgentListener[LineDelivered]):
    """A silent worker reported to the agent is marked as reported on its row, so its silence is reported once; its next send, notify or report starts a new span."""

    def __init__(self, workers: Workers) -> None:
        self.workers = workers

    def handle(self, event: LineDelivered) -> None:
        if event.nudge != WorkersNudges.SILENT_WORKER.key:
            return
        worker = self.workers.find(int(event.values["n"]))
        self.workers.touch(worker, Actor.system(), silence=worker.silence.reported())
