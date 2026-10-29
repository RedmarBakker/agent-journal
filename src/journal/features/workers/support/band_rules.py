from journal.features.workers.fitness_options import FitnessOptions
from journal.features.workers.support.band_rule import BandRule
from journal.features.workers.support.load_item import LoadItem
from journal.models.agent import Agent
from journal.models.support.agent_load import AgentLoad
from journal.models.support.pressure_band import PressureBand
from journal.repositories.setting_rows import SettingRows
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE

MODE_LEVELS = {
    ORCHESTRATOR_MODE: (FitnessOptions.ORCHESTRATOR_HIGH_ENTRY, FitnessOptions.ORCHESTRATOR_HIGH_EXIT, FitnessOptions.ORCHESTRATOR_LOW_ENTRY, FitnessOptions.ORCHESTRATOR_LOW_EXIT),
    BUILDER_MODE: (FitnessOptions.BUILDER_HIGH_ENTRY, FitnessOptions.BUILDER_HIGH_EXIT, FitnessOptions.BUILDER_LOW_ENTRY, FitnessOptions.BUILDER_LOW_EXIT),
}


class BandRules:
    """The band each mode with workers moves by, built from the settings: the orchestrator's and the builder's levels, the least minutes in a band and the minutes an empty queue takes to leave high; solo has no band, and a mode's first band, after the upgrade or any change of mode, is normal."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def band(self, agent: Agent, mode: str, work_queue: AgentLoad, work_items: list[LoadItem], time: float) -> PressureBand:
        if mode not in MODE_LEVELS:
            return PressureBand.NONE
        if agent.band == PressureBand.NONE or agent.measures.mode != mode:
            return PressureBand.NORMAL
        high_entry, high_exit, low_entry, low_exit = (self.settings.decimal(option) for option in MODE_LEVELS[mode])
        rule = BandRule(high_entry, high_exit, low_entry, low_exit, self.settings.decimal(FitnessOptions.BAND_MINUTES) * 60, self.settings.decimal(FitnessOptions.EMPTY_QUEUE_MINUTES) * 60)
        return rule.moved(agent.band, work_queue.rho, time - agent.band_changed_at, self.empty_seconds(work_items, time))

    @staticmethod
    def empty_seconds(items: list[LoadItem], time: float) -> float:
        if any(item.is_waiting(time) for item in items):
            return 0.0
        ends = [max(item.cleared_at, item.ended_at) for item in items]
        return time - max(ends) if ends else time
