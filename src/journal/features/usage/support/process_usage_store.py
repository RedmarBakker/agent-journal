from dataclasses import asdict

from journal.models.agent import Agent
from journal.models.worker import Worker
from journal.support.process_usage import ProcessUsage


class ProcessUsageStore:
    """What each agent's and each worker's processes took of the machine at the last sample, kept in memory between samples: the main agent's program and the shell commands its session started, a worker's run and its shell commands."""

    def __init__(self) -> None:
        self.agents: dict[tuple[int, str], ProcessUsage] = {}
        self.workers: dict[int, ProcessUsage] = {}

    def replaced(self, agents: dict[tuple[int, str], ProcessUsage], workers: dict[int, ProcessUsage]) -> None:
        self.agents, self.workers = agents, workers

    def agent_fields(self, agent: Agent) -> dict | None:
        usage = self.agents.get((agent.environment_id, agent.session))
        return asdict(usage) if usage else None

    def worker_fields(self, worker: Worker) -> dict | None:
        usage = self.workers.get(worker.row_id)
        return asdict(usage) if usage else None
