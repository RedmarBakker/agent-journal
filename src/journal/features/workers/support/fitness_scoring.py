from journal.features.workers.fitness_options import FitnessOptions
from journal.features.workers.support.fitness_score import FitnessScore
from journal.features.workers.support.mode_measures import ModeMeasures
from journal.models.agent import Agent
from journal.repositories.setting_rows import SettingRows


class FitnessScoring:
    """An agent's fitness scored from the states of its mode's measures, once the mode has been measured for the warm-up the user set."""

    def __init__(self, settings: SettingRows, measures: ModeMeasures) -> None:
        self.settings, self.measures = settings, measures

    def scored(self, agent: Agent) -> FitnessScore:
        return ModeMeasures.scored(agent.measures, self.measures.specs(agent.measures.mode), self.settings.decimal(FitnessOptions.SCORE_WARMUP_MINUTES) * 60)
