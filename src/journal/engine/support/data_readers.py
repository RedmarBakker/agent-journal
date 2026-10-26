from journal.events.feature_data import FeatureData
from journal.models.agent import Agent
from journal.engine.support.data_reader import DataReader
from journal.engine.support.feature_parts import FeatureParts
from journal.engine.support.feature_registry import FeatureRegistry
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes


class DataReaders:
    """Every feature's data reader by the feature's name; builds the feature data an event carries for the agent concerned, each part read when a listener first asks for it, a helper's refusing the parts of features its file does not turn on."""

    def __init__(self, readers: dict[str, DataReader], scope: Scope, stages: StageTimes, features: FeatureRegistry) -> None:
        self.readers, self.scope, self.stages, self.features = readers, scope, stages, features

    def agent_data(self, agent: Agent) -> FeatureData:
        return FeatureData(FeatureParts(self.readers, agent, self.scope, self.stages, self.features.refused_parts(agent.role)))
