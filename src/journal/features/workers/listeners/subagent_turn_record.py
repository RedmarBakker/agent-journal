from journal.support.researcher_session import ResearcherSession
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.subagent_chat import SubagentChat
from journal.repositories.subagents import Subagents


class SubagentTurnRecord(AgentListener[AgentEvent]):
    """At each of a subagent's hooks, those on its own row and its end on the main agent's, after the hook is answered, the text it wrote since the last read becomes its messages, the first read starting with its prompt."""


    def __init__(self, chat: SubagentChat, subagents: Subagents) -> None:
        self.chat, self.subagents = chat, subagents

    def handle(self, event: AgentEvent) -> None:
        session, agent_id = (event.session, event.subagent) if event.subagent else ResearcherSession.parts(event.session)
        for subagent in self.subagents.session_subagent(session, agent_id):
            self.chat.read(subagent)
