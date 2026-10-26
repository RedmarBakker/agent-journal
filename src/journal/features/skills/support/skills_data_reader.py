from journal.features.skills.support.skill_card import SkillCard
from journal.features.skills.support.skills_data import SkillsData
from journal.models.agent import Agent
from journal.features.skills.support.skill_files import SkillFiles


class SkillsDataReader:
    """Reads the skills feature's part of the feature data for an agent."""

    def __init__(self, files: SkillFiles) -> None:
        self.files = files

    def read(self, agent: Agent) -> SkillsData:
        cards = tuple(SkillCard(skill.name, self.files.relative_path(skill), self.files.digest(skill), skill.keywords, skill.required_states, skill.commands) for skill in self.files.catalogue())
        return SkillsData(skills_due=tuple(agent.skills_due), loaded=dict(agent.skills_loaded), skills=cards)
