from journal.engine.support.lazy_facts import LazyFacts
from journal.models.agent import Agent
from journal.repositories.scope import Scope
from journal.repositories.triggers import Triggers
from journal.support.stage_times import StageTimes


class TriggersDataReader:
    """Reads the triggers feature's part of the feature data for an agent the first time a listener asks for it, with the fields TriggersData names."""

    def __init__(self, triggers: Triggers, scope: Scope, stages: StageTimes) -> None:
        self.triggers, self.scope, self.stages = triggers, scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        return LazyFacts("triggers", {"triggers": lambda: tuple(self.triggers.all())}, lambda: self.scope.environment(agent.environment_id), self.stages)
