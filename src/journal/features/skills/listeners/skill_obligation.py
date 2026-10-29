from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.session_started import SessionStarted
from journal.events.agent_listener import AgentListener
from journal.features.skills.support.requirements import Requirements
from journal.features.skills.support.skills_data_reader import SkillsDataReader
from journal.features.skills.skills_conduct import start_option
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows


class SkillObligation(AgentListener[AgentEvent]):
    """The skills a start or a prompt calls for, as the skills conduct names them, are recorded as required on the agent's row, beside those already required, so a write waits until they are read."""

    def __init__(self, agents: Agents, reader: SkillsDataReader, settings: SettingRows, requirements: Requirements) -> None:
        self.agents, self.reader, self.settings, self.requirements = agents, reader, settings, requirements

    def handle(self, event: AgentEvent) -> None:
        if not isinstance(event, (SessionStarted, PromptSubmitted)):
            return
        agent = self.agents.newest_row(event.agent)
        data = self.reader.read(agent)
        due = data.mentioned(event.users_words()) if isinstance(event, PromptSubmitted) else data.start_debts(self.settings.texts(start_option(event)), agent.state)
        self.requirements.obligation_names_added(agent, tuple(card.name for card in due))
