from journal.features.workers.support.fitness_scoring import FitnessScoring
from journal.models.agent import Agent
from journal.repositories.agents import Agents


class DroppedScore:
    """The fitness score of the agent whose session a drop fell on, after the drop: the measured score, or a hundred less the drop's points while the agent has too few tool uses to be scored."""

    def __init__(self, agents: Agents, scoring: FitnessScoring) -> None:
        self.agents, self.scoring = agents, scoring

    def session_score(self, session: str) -> int:
        rows = self.agents.session_rows(session)
        return self.score(rows[0]) if rows else 0

    def score(self, agent: Agent) -> int:
        scored = self.scoring.scored(agent)
        return scored.score if scored.is_measured else max(0, 100 - agent.report_use.drop_points)
