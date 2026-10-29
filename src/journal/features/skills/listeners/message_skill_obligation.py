from journal.events.listener import Listener
from journal.events.rows.message_read import MessageRead
from journal.features.skills.support.requirements import Requirements
from journal.features.skills.support.skills_data_reader import SkillsDataReader
from journal.repositories.agents import Agents
from journal.support.actor import Actor


class MessageSkillObligation(Listener[MessageRead]):
    """The skills a user's message names by their words are due for the main agent who read it, as a prompt's are, so its next write waits until they are read."""

    def __init__(self, agents: Agents, reader: SkillsDataReader, requirements: Requirements) -> None:
        self.agents, self.reader, self.requirements = agents, reader, requirements

    def handle(self, event: MessageRead) -> None:
        reader = Actor.parse(event.actor)
        if not event.user_text or not reader.is_agent_actor():
            return
        agent = self.agents.active_main_agent(reader.id)
        if agent is not None:
            self.requirements.obligation_names_added(agent, tuple(card.name for card in self.reader.read(agent).mentioned(event.user_text)))
