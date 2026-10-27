from journal.engine.support.session_agents import SessionAgents
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.sequences.support.announced_starts import AnnouncedStarts
from journal.repositories.sequences import Sequences


class CallStart(AgentListener[ToolFinished]):
    """A tool call of the main agent's own that a sequence's command, file, file-text or tool trigger waits for starts that sequence; a worker's or a subagent's call starts nothing."""

    def __init__(self, sequences: Sequences, sessions: SessionAgents, starts: AnnouncedStarts) -> None:
        self.sequences, self.sessions, self.starts = sequences, sessions, starts

    def handle(self, event: ToolFinished) -> None:
        if event.subagent or not self.sessions.agent(event.session, event.environment_id).is_main():
            return
        for sequence in self.sequences.called_sequences(event.call):
            self.starts.start(sequence, event.session, event.environment_id)
