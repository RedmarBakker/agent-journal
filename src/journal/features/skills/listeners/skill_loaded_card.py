from journal.chat.moment_cards import MomentCards
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.skills.support.skill_files import SkillFiles
from journal.support.card_type import CardType


class SkillLoadedCard(AgentListener[ToolFinished]):
    """Every skill a tool loaded, ours or another's, shows a mark in the chat, after the hook has answered."""

    def __init__(self, files: SkillFiles, cards: MomentCards) -> None:
        self.files, self.cards = files, cards

    def handle(self, event: ToolFinished) -> None:
        names = [skill.name for skill in self.files.loaded_skills(event.call)] + list(self.files.other_skill_names(event.call))
        for name in names:
            self.cards.show(event.environment_id, event.session, f"Skill {name} loaded", name, type_name="skill", shows=CardType.SKILLS)
