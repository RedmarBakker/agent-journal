from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.fitness_levels import FitnessLevels
from journal.features.workers.support.fitness_scoring import FitnessScoring
from journal.features.workers.fitness_options import FitnessOptions
from journal.features.workers.workers_options import WorkersOptions
from journal.support.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor


class FitnessLevelRecord(AgentListener[ToolFinished]):
    """After each tool use of the main agent, the level its fitness stands on is kept on its row in a field of its own, never in the data of the state on top of its stack, which every state change writes over, so a fall past a lower level is told once and a rise lets the levels above be told again."""

    def __init__(self, agents: Agents, scoring: FitnessScoring, settings: SettingRows) -> None:
        self.agents, self.scoring, self.settings = agents, scoring, settings

    def handle(self, event: ToolFinished) -> None:
        rows = self.agents.session_rows(event.session)
        if event.subagent or not rows or rows[0].role != AgentRole.MAIN:
            return
        fitness = self.scoring.scored(rows[0])
        if fitness is None or not fitness.is_measured:
            return
        step = self.settings.integer(FitnessOptions.LEVEL_STEP)
        level = FitnessLevels.standing(fitness.score, step) if step > 0 else 100
        if level != rows[0].fitness_level:
            self.agents.save(rows[0].with_(fitness_level=level), Actor.system())
