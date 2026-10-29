from pathlib import Path

from journal.engine.job import Job
from journal.features.shell.support.output_files import OutputFiles
from journal.features.usage.support.process_usage_store import ProcessUsageStore
from journal.models.environment import Environment
from journal.repositories.agents import Agents
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.supervisor_link import SupervisorLink
from journal.support.process_usage import ProcessUsage


class ProcessUsageWatch(Job):
    """Every few seconds the process groups of each environment's main agent (its program in front and the shell commands of its session) and of each running worker (its run and the shell commands of its session) are read in one ps through one supervisor, ps seeing every process of the machine, and kept for the agents' and the workers' cells."""

    interval_seconds = 5.0

    def __init__(self, supervisor: SupervisorLink, environments: Environments, agents: Agents, workers: Workers, outputs: CommandOutputs, scope: Scope, store: ProcessUsageStore) -> None:
        self.supervisor, self.environments, self.agents, self.workers, self.outputs, self.scope, self.store = supervisor, environments, agents, workers, outputs, scope, store

    def tick(self, time: float) -> None:
        supervised_environments = self.supervisor.running(self.environments.all())
        if not supervised_environments:
            return
        agent_groups, worker_groups = self.agent_groups(supervised_environments), self.worker_groups(supervised_environments)
        usage = self.supervisor.usage(supervised_environments[0].row_id, {group for groups in [*agent_groups.values(), *worker_groups.values()] for group in groups})
        self.store.replaced({key: self.summed(groups, usage) for key, groups in agent_groups.items()}, {key: self.summed(groups, usage) for key, groups in worker_groups.items()})

    def agent_groups(self, environments: list[Environment]) -> dict[tuple[int, str], set[int]]:
        groups: dict[tuple[int, str], set[int]] = {}
        for environment in environments:
            with self.scope.environment(environment.row_id):
                agent = self.agents.current()
            if agent is not None:
                front = {process.pid for process in self.supervisor.processes(environment.row_id) if process.front and process.is_active}
                groups[(environment.row_id, agent.session)] = front | self.shell_groups(environment.row_id, agent.session)
        return groups

    def worker_groups(self, environments: list[Environment]) -> dict[int, set[int]]:
        groups: dict[int, set[int]] = {}
        for environment in environments:
            with self.scope.environment(environment.row_id):
                dispatched_workers = self.workers.running_workers()
            for worker in dispatched_workers:
                groups[worker.row_id] = {worker.pid} - {0} | self.shell_groups(environment.row_id, worker.session)
        return groups

    def shell_groups(self, environment_id: int, session: str) -> set[int]:
        return {OutputFiles(Path(output.folder)).shell_pid() for output in self.outputs.running_session_outputs(environment_id, session)} - {0}

    @staticmethod
    def summed(groups: set[int], usage: dict[int, ProcessUsage]) -> ProcessUsage:
        return ProcessUsage.total([usage[group] for group in groups if group in usage])
