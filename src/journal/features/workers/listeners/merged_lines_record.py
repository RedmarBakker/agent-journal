from journal.events.listener import Listener
from journal.events.moments.worker_work_merged import WorkerWorkMerged
from journal.repositories.agents import Agents
from journal.support.actor import Actor


class MergedLinesRecord(Listener[WorkerWorkMerged]):
    """The lines a worker's merge brought in are kept on its dispatcher's row, which the builder's share of its own code is weighed against."""

    def __init__(self, agents: Agents) -> None:
        self.agents = agents

    def handle(self, event: WorkerWorkMerged) -> None:
        agent = self.agents.active_main_agent(event.dispatcher) if event.dispatcher else None
        if agent is not None and event.lines:
            self.agents.rewritten(agent, Actor.system(), lambda current: current.lines_merged(event.lines))
