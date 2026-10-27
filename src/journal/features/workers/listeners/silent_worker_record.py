from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class SilentWorkerRecord(AgentListener[Ticked]):
    """A running worker silent past its span is marked on its row at the tick, and the mark raises WorkerSilent, which names it to its dispatcher once; once at the span and once more at twice the span, its next send, notify or report starting a new span."""

    blocking = True

    def __init__(self, workers: Workers) -> None:
        self.workers = workers

    def handle(self, event: Ticked) -> None:
        for worker in self.workers.running_workers():
            if worker.dispatcher == event.session and worker.is_silent(event.time):
                self.workers.mark_silence(worker, event.time, Actor.system())
