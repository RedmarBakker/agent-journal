from journal.chat.moment_cards import MomentCards
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.support.skill import Skill
from journal.features.skills.support.skill_files import SkillFiles
from journal.support.actor import Actor
from journal.repositories.agents import Agents
from journal.support.card_type import CardType
from journal.engine.clock import Clock


class SkillCard(AgentListener[ToolFinished]):
    """A read of our skill files, by the read tool, a shell line or the skill tool, is remembered on the agent with each file's hash, added to what it holds under the write lock, so two reads sent together are both stored; every skill loaded, ours or another's, shows a card in the chat."""

    blocking = True

    def __init__(self, agents: Agents, files: SkillFiles, cards: MomentCards, clock: Clock) -> None:
        self.agents, self.files, self.cards, self.clock = agents, files, cards, clock

    def handle(self, event: ToolFinished) -> None:
        for skill in self.files.loaded_skills(event.call):
            self.loaded(event, skill)
        for name in self.files.other_skill_names(event.call):
            self.cards.show(event.environment_id, event.session, f"Skill {name} loaded", name, type_name="skill", shows=CardType.SKILLS)

    def loaded(self, event: ToolFinished, skill: Skill) -> None:
        digest = self.files.digest(skill)
        self.agents.rewritten(self.agents.session_agent(event.session), Actor.system(), lambda time: time.skill_read(skill.name, digest, self.clock.time()))
        self.cards.show(event.environment_id, event.session, f"Skill {skill.name} loaded", skill.name, type_name="skill", shows=CardType.SKILLS)
