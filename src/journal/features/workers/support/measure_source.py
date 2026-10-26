from dataclasses import dataclass

from journal.features.workers.support.free_place_measure import FreePlaceMeasure
from journal.models.agent import Agent

SHARE_SECONDS = 7200.0
SHARE_LEAST_LINES = 40
HOUR_SECONDS = 3600.0


@dataclass(frozen=True)
class MeasureSource:
    """What one measuring of the agent reads, its row with the two queues just measured and the free places, with the raw value of each measure; None where there was nothing to measure."""

    agent: Agent
    time: float
    free_places: FreePlaceMeasure

    def code_share(self) -> float | None:
        agent_lines, worker_lines = self.agent.committed_total(self.time, SHARE_SECONDS), self.agent.merged_total(self.time, SHARE_SECONDS)
        return agent_lines / (agent_lines + worker_lines) if agent_lines + worker_lines >= SHARE_LEAST_LINES else None

    def high_queue_minutes(self) -> float | None:
        return self.agent.work_queue.over_minutes if self.agent.work_queue.is_measured() else None

    def clearing_wait(self) -> float | None:
        return self.agent.work_queue.wait_minutes if self.agent.work_queue.clearings_counted else None

    def idle_place_minutes(self) -> float | None:
        return self.free_places.minutes(self.time - HOUR_SECONDS, self.time)

    def first_report_count(self) -> float | None:
        return float(self.agent.first_report_count(self.time, HOUR_SECONDS))

    def dispatches_against(self) -> float | None:
        return float(self.agent.work_queue.dispatches_against) if self.agent.work_queue.is_measured() else None

    def message_wait_minutes(self) -> float | None:
        return self.agent.message_queue.over_minutes if self.agent.message_queue.is_measured() else None
