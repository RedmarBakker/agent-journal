from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class SilentWorkerRecord(AgentListener[Ticked]):
    """A silent worker named to its dispatcher on a tick is marked on its row in the same tick, right after the machine answered it, so the next tick sees it named however soon it comes; once at the span and once more at twice the span, its next send, notify or report starting a new span."""

    blocking = True

    def __init__(self, workers: Workers) -> None:
        self.workers = workers

    def handle(self, event: Ticked) -> None:
        for worker in self.workers.running_workers():
            if worker.dispatcher == event.session and worker.is_silent(event.time):
                self.workers.touch(worker, Actor.system(), silence=worker.silence.named(event.time))
