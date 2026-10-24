from journal.engine.demand_progress import DemandProgress
from journal.engine.demand_tracker import DemandTracker
from journal.models.agent import Agent


class DemandsReader:
    """Reads the agent's progress on its demands from the engine's tracker."""

    def __init__(self, tracker: DemandTracker) -> None:
        self.tracker = tracker

    def read(self, agent: Agent) -> tuple[DemandProgress, ...]:
        return self.tracker.progress(agent.session)
