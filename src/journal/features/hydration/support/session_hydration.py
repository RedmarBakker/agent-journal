from datetime import datetime, timezone

from journal.config import Config
from journal.features.hydration.support.transcript_chat import TranscriptChat
from journal.models.agent import Agent
from journal.models.agent_role import AgentRole
from journal.models.environment import Environment
from journal.models.message import Message
from journal.providers.providers import Providers
from journal.repositories.agents import Agents
from journal.repositories.messages import Messages
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.rejection import Rejection


class SessionHydration:
    """Fills a new environment's chat from a conversation an agent program kept for this project, each message at its own time and none of them told to the agent as new, and keeps the session as the environment's ended agent, so its first launch carries the conversation on; a line at the end says where the chat came from, until the first agent there has been asked to read it."""

    def __init__(self, config: Config, providers: Providers, messages: Messages, agents: Agents, scope: Scope) -> None:
        self.config, self.providers, self.messages, self.agents, self.scope = config, providers, messages, agents, scope

    def hydrate(self, environment: Environment, provider: str, session: str, actor: Actor) -> int:
        program = self.providers.lookup(provider)
        path = program.transcript(self.config.root, session)
        if path is None:
            raise Rejection(f"no {provider} session {session} is kept for this project on this machine")
        rows = TranscriptChat(session).read(program.turns(path))
        last = rows[-1].time if rows else path.stat().st_mtime
        with self.scope.environment(environment.row_id):
            for row in rows:
                self.messages.imported(row.message.with_(environment_id=environment.row_id), self.moment(row.time), actor)
            self.agents.imported(Agent(environment_id=environment.row_id, session=session, provider=provider, state="ended", role=AgentRole.MAIN), self.moment(last), actor)
            self.messages.imported(Message.hydration(provider, session, f"This chat was filled from {program.title} session {session[:8]}: {len(rows)} messages.").with_(environment_id=environment.row_id), self.moment(last), actor)
        return len(rows)

    @staticmethod
    def moment(time: float) -> datetime:
        return datetime.fromtimestamp(time, timezone.utc)
