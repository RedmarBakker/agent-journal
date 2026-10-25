from journal.features.reviewing.reviewing_options import ReviewingOptions
from dataclasses import replace

from journal.features.workers.support.fitness_score import FitnessScore
from journal.features.workers.support.own_share_limits import OwnShareLimits
from journal.features.workers.support.tool_use_counts import ToolUseCounts
from journal.features.workers.workers_options import WorkersOptions
from journal.features.workers.workers_profiles import WorkersProfiles
from journal.models.agent import Agent
from journal.repositories.setting_rows import SettingRows


class FitnessScoring:
    """An agent's fitness scored against the profile of the work mode the user set, the reviewed one while the reviewer is on; none in a mode with no profile."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def scored(self, agent: Agent) -> FitnessScore | None:
        profile = (WorkersProfiles.reviewed_mode_profile if self.settings.option(ReviewingOptions.REVIEWER) else WorkersProfiles.mode_profile)(str(self.settings.option(WorkersOptions.MODE)))
        limits = OwnShareLimits(self.settings.decimal(WorkersOptions.OWN_SHARE_FULL), self.settings.decimal(WorkersOptions.OWN_SHARE_ZERO), self.settings.integer(WorkersOptions.OWN_SHARE_WEIGHT))
        return profile.scored(replace(ToolUseCounts.counted(agent), own_share=limits)) if profile else None
