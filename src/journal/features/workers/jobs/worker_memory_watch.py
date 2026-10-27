from journal.engine.job import Job
from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.workers_options import WorkersOptions
from journal.models.worker import Worker
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.workers import Workers
from journal.supervisor_link import SupervisorLink
from journal.support.actor import Actor

MEGABYTE = 1024 * 1024


class WorkerMemoryWatch(Job):
    """Every five seconds the supervisor of each environment reports the resident memory of its workers' process trees: a worker past the warning budget is named once to the agent that sent it, and one past the limit, or the one using the most while all of them together pass the total, is stopped with the reason written on it."""

    interval_seconds = 5.0

    def __init__(self, workers: Workers, supervisor: SupervisorLink, actions: WorkerActions, settings: SettingRows, scope: Scope) -> None:
        self.workers, self.supervisor, self.actions, self.settings, self.scope = workers, supervisor, actions, settings, scope
        self.warned: set[int] = set()

    def tick(self, time: float) -> None:
        running = self.workers.running_everywhere()
        for environment_id in sorted({worker.environment_id for worker in running}):
            with self.scope.environment(environment_id):
                self.measured([worker for worker in running if worker.environment_id == environment_id], self.supervisor.memory(environment_id), time)

    def measured(self, workers: list[Worker], memory: dict[int, int], time: float) -> None:
        sizes = {worker.id: memory[worker.pid] // MEGABYTE for worker in workers if worker.pid in memory}
        warning, limit, total = (self.settings.integer(option) for option in (WorkersOptions.MEMORY_WARNING_MEGABYTES, WorkersOptions.MEMORY_LIMIT_MEGABYTES, WorkersOptions.MEMORY_TOTAL_MEGABYTES))
        for worker in (worker for worker in workers if worker.id in sizes):
            if sizes[worker.id] > limit:
                self.actions.stop(worker.id, f"its processes used {sizes.pop(worker.id)} MB, past the limit of {limit} MB", Actor.system())
            elif sizes[worker.id] > warning and worker.id not in self.warned:
                self.warned.add(worker.id)
                self.workers.save(worker.over_memory(time, sizes[worker.id], warning), Actor.system())
        if total and sum(sizes.values()) > total:
            largest = max(sizes, key=sizes.__getitem__)
            self.actions.stop(largest, f"all workers' processes together used {sum(sizes.values())} MB, past the total of {total} MB, and it used the most", Actor.system())
