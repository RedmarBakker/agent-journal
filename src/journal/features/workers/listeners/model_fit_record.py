from functools import partial

from journal.events.listener import Listener
from journal.support.listener_queue import ListenerQueue
from journal.events.rows.worker_merged import WorkerMerged
from journal.features.workers.support.merged_work import MergedWork
from journal.providers.providers import Providers
from journal.repositories.agents import Agents
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class ModelFitRecord(Listener[WorkerMerged]):
    """A worker's merged work is measured for how complex it was and set against the model it ran on, kept on the worker, and on the agent that sent it among the fits of its newest merged jobs, which its fitness counts; on the deferred worker after the merge has answered, so nothing it does touches the merge."""

    def __init__(self, deferred: ListenerQueue, workers: Workers, agents: Agents, work: MergedWork, providers: Providers) -> None:
        self.deferred, self.workers, self.agents, self.work, self.providers = deferred, workers, agents, work, providers

    def handle(self, event: WorkerMerged) -> None:
        self.deferred.add(partial(self.measured, event))

    def measured(self, event: WorkerMerged) -> None:
        worker = self.workers.find(event.worker.id)
        complexity = self.work.complexity(worker)
        fit = complexity.fit(self.providers.lookup(worker.provider).tier(worker.model))
        self.workers.save(worker.model_measured(fit, complexity.send_backs, event.time), Actor.system())
        dispatcher = self.agents.active_main_agent(worker.dispatcher) if worker.dispatcher and fit.measured else None
        if dispatcher is not None:
            self.agents.save(dispatcher.model_fit_kept(worker.row_id, fit.measured), Actor.system())
