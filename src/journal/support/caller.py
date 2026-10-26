from dataclasses import dataclass, replace

from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.support.rejection import Rejection

LOCAL_USER = 1

AGENT_SHELL = "JOURNAL_AGENT_SHELL"
# who runs a shell: agent, sub-agent, or a sent agent as its actor stamp, worker:12, verifier:3 or reviewer:4, which proves itself with the token beside it
ACTOR = "JOURNAL_ACTOR"
ACTOR_TOKEN = "JOURNAL_ACTOR_TOKEN"

AGENT_REQUIRED = "no agent runs this: only an agent's own session can"


@dataclass(frozen=True)
class Caller:
    """Where a command runs and who runs it: the user, an agent by its session and provider, an agent's shell that names no session, a plugin by its name, a worker, a verifier or a reviewer by its number, its session when its program names one, and its provider, or a subagent of any of these; its role says which helper runs it, the main agent's role standing for the main agent, the user and a plugin alike, and its session role the role of the agent whose session it runs in, a subagent's being its parent's, and the person is the user's account number on a shared journal."""

    environment: str
    session: str | None = None
    provider: str | None = None
    plugin_name: str | None = None
    worker_number: int | None = None
    verifier_number: int | None = None
    reviewer_number: int | None = None
    subagent: bool = False
    person: int = LOCAL_USER

    @classmethod
    def user(cls, environment: str) -> "Caller":
        return cls(environment)

    @classmethod
    def agent(cls, environment: str, session: str, provider: str) -> "Caller":
        return cls(environment, session, provider)

    @classmethod
    def shell(cls, environment: str, provider: str) -> "Caller":
        return cls(environment, provider=provider)

    @classmethod
    def plugin(cls, environment: str, name: str) -> "Caller":
        return cls(environment, plugin_name=name)

    @classmethod
    def worker(cls, environment: str, number: int, session: str | None, provider: str) -> "Caller":
        return cls(environment, session, provider, worker_number=number)

    @classmethod
    def verifier(cls, environment: str, number: int, session: str | None, provider: str) -> "Caller":
        return cls(environment, session, provider, verifier_number=number)

    @classmethod
    def reviewer(cls, environment: str, number: int, session: str | None, provider: str) -> "Caller":
        return cls(environment, session, provider, reviewer_number=number)

    def subagent_caller(self) -> "Caller":
        return replace(self, subagent=True)

    @property
    def role(self) -> AgentRole:
        return AgentRole.SUBAGENT if self.subagent else self.session_role

    @property
    def session_role(self) -> AgentRole:
        if self.worker_number is not None:
            return AgentRole.WORKER
        if self.verifier_number is not None:
            return AgentRole.VERIFIER
        if self.reviewer_number is not None:
            return AgentRole.REVIEWER
        return AgentRole.MAIN

    def is_main_agent(self) -> bool:
        return self.role == AgentRole.MAIN and self.plugin_name is None and (self.session is not None or self.provider is not None)

    @property
    def actor(self) -> Actor:
        if self.plugin_name is not None:
            return Actor.plugin(self.plugin_name)
        if self.worker_number is not None:
            return Actor.worker(self.worker_number)
        if self.verifier_number is not None:
            return Actor.verifier(self.verifier_number)
        if self.reviewer_number is not None:
            return Actor.reviewer(self.reviewer_number)
        return Actor.user(self.person) if self.session is None else Actor.agent(self.session)

    @property
    def agent_session(self) -> str:
        if self.session is None:
            raise Rejection(AGENT_REQUIRED)
        return self.session

    @property
    def agent_provider(self) -> str:
        if self.provider is None:
            raise Rejection(AGENT_REQUIRED)
        return self.provider

    def is_unnamed_agent(self) -> bool:
        return self.provider is not None and self.session is None and self.worker_number is None and self.verifier_number is None and self.reviewer_number is None
