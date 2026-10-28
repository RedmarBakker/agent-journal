from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.events.blocking import Blocking
from journal.support.skill import Skill
from journal.features.skills.support.skill_files import SkillFiles
from journal.support.actor import Actor
from journal.repositories.agents import Agents
from journal.engine.clock import Clock


class SkillReadRecord(AgentListener[ToolFinished]):
    """A read of our skill files, by the read tool, a shell line or the skill tool, is remembered on the agent with each file's hash before the hook answers, added to what it holds under the write lock, so two reads sent together are both stored and the next write a skill held goes through."""

    blocking = Blocking.NEXT_DECISION

    def __init__(self, agents: Agents, files: SkillFiles, clock: Clock) -> None:
        self.agents, self.files, self.clock = agents, files, clock

    def handle(self, event: ToolFinished) -> None:
        for skill in self.files.loaded_skills(event.call):
            self.loaded(event, skill)

    def loaded(self, event: ToolFinished, skill: Skill) -> None:
        digest = self.files.digest(skill)
        self.agents.rewritten(self.agents.session_agent(event.session), Actor.system(), lambda time: time.skill_read(skill.name, digest, self.clock.time()))
