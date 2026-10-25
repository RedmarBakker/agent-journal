from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent
from journal.features.registry import Registry
from journal.features.skills.support.requirements import Requirements
from journal.repositories.agents import Agents


class SkillTriggers(Listener[RowEvent]):
    """An event a skill names as calling for it makes that skill due for the environment's main agent, unless the agent read it since its last compaction."""

    def __init__(self, registry: Registry, requirements: Requirements, agents: Agents) -> None:
        self.registry, self.requirements, self.agents = registry, requirements, agents

    def handle(self, event: RowEvent) -> None:
        skills = [skill for skill in self.registry.skills() if isinstance(event, skill.events)]
        if not skills:
            return
        for agent in self.agents.main_scoped(event.environment_id):
            self.requirements.obligation(agent, self.requirements.obligations(agent, skills))
