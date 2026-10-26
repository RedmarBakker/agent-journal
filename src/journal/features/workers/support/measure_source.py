from dataclasses import dataclass
from datetime import datetime, timezone

from journal.features.workers.support.free_place_measure import FreePlaceMeasure
from journal.features.workers.support.active_worker_measure import ActiveWorkerMeasure
from journal.models.agent import Agent
from journal.repositories.tasks import Tasks

SHARE_SECONDS = 3600.0
COMPLETION_SECONDS = 7200.0
SHARE_LEAST_LINES = 40
HOUR_SECONDS = 3600.0
REPORT_SECONDS = 7200.0
LEAST_MERGES = 2


@dataclass(frozen=True)
class MeasureSource:
    """What one measuring of the agent reads, its row with the two queues just measured, the free places, the active workers and the tasks completed, with the raw value of each measure; None where there was nothing to measure."""

    agent: Agent
    time: float
    free_places: FreePlaceMeasure
    active_workers: ActiveWorkerMeasure
    tasks: Tasks

    def code_share(self) -> float | None:
        agent_lines, worker_lines = self.agent.authored_total(self.time, SHARE_SECONDS), self.agent.merged_total(self.time, SHARE_SECONDS)
        return agent_lines / (agent_lines + worker_lines) if agent_lines + worker_lines >= SHARE_LEAST_LINES else None

    def active_worker_mean(self) -> float | None:
        return self.active_workers.mean(self.time - HOUR_SECONDS, self.time)

    def completion_rate(self) -> float | None:
        moments = (datetime.fromtimestamp(self.time - COMPLETION_SECONDS, timezone.utc), datetime.fromtimestamp(self.time, timezone.utc))
        return len(self.tasks.recent_completions(*moments)) / (COMPLETION_SECONDS / 3600)

    def high_queue_minutes(self) -> float | None:
        return self.agent.work_queue.over_minutes if self.agent.work_queue.is_measured() else None

    def clearing_wait(self) -> float | None:
        return self.agent.work_queue.oldest_wait_minutes if self.agent.work_queue.is_measured() else None

    def delegation(self) -> float | None:
        agent_lines, worker_lines = self.agent.authored_total(self.time, HOUR_SECONDS), self.agent.merged_total(self.time, HOUR_SECONDS)
        enough = agent_lines + worker_lines and self.agent.merge_count(self.time, HOUR_SECONDS) >= LEAST_MERGES
        return agent_lines / (agent_lines + worker_lines) if enough else None

    def report_share(self) -> float | None:
        merges = self.agent.merge_count(self.time, REPORT_SECONDS)
        return self.agent.first_report_count(self.time, REPORT_SECONDS) / merges if merges else None

    def oldest_first_share(self) -> float | None:
        queue = self.agent.work_queue
        return queue.oldest_first / queue.clearings_counted if queue.clearings_counted else None

    def rejection_share(self) -> float | None:
        queue = self.agent.work_queue
        return queue.removals / (queue.removals + queue.clearings_counted) if queue.removals + queue.clearings_counted else None

    def idle_place_minutes(self) -> float | None:
        return self.free_places.minutes(self.time - HOUR_SECONDS, self.time)

    def message_wait_minutes(self) -> float | None:
        return self.agent.message_queue.over_minutes if self.agent.message_queue.is_measured() else None
