from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.workers_options import WorkersOptions
from journal.models.agent_role import AgentRole
from journal.models.support.queue_use import QueueUse
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.agents import Agents
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class QueueUseRecord(AgentListener[ToolFinished]):
    """After each tool use of the orchestrator, its workers' queues are measured: of those with merges over the window, the ones whose queue stands empty while tasks are open, and the ones holding more than they drain in the hours set; kept on its row for the fitness, in orchestrator mode only."""

    def __init__(self, agents: Agents, workers: Workers, tasks: Tasks, plans: Plans, settings: SettingRows) -> None:
        self.agents, self.workers, self.tasks, self.plans, self.settings = agents, workers, tasks, plans, settings

    def handle(self, event: ToolFinished) -> None:
        if event.subagent or self.settings.option(WorkersOptions.MODE) != "orchestrator":
            return
        rows = self.agents.session_rows(event.session)
        if not rows or rows[0].role != AgentRole.MAIN:
            return
        window_minutes = self.settings.decimal(WorkersOptions.QUEUE_WINDOW)
        drains = {worker.row_id: self.merge_count(worker, event.time, window_minutes) for worker in self.workers.matching(dispatcher=event.session)}
        counted = [worker_id for worker_id, merges in drains.items() if merges]
        open_tasks = self.plans.open_work_count()
        depths = {worker_id: len(self.tasks.queue(Ref("workers", worker_id))) for worker_id in counted}
        hourly = {worker_id: drains[worker_id] * 60 / max(window_minutes, 1.0) for worker_id in counted}
        use = QueueUse(len(counted), sum(1 for worker_id in counted if open_tasks and not depths[worker_id]), sum(1 for worker_id in counted if depths[worker_id] > hourly[worker_id] * self.settings.decimal(WorkersOptions.QUEUE_DRAIN_HOURS)))
        if use != rows[0].queue_use:
            self.agents.save(rows[0].with_(queue_use=use), Actor.system())

    @staticmethod
    def merge_count(worker: Worker, time: float, window_minutes: float) -> int:
        return sum(1 for word, moment in worker.moves.steps if word == "merged" and time - moment <= window_minutes * 60)
