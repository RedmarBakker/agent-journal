from dataclasses import replace
from functools import cache
from typing import Callable

from journal.models.agent import Agent
from journal.repositories.environments import Environments
from journal.repositories.origin import Origin
from journal.repositories.scope_binding import CURRENT, ScopeBinding
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.support.caller import AGENT_REQUIRED
from journal.support.rejection import Rejection
from journal.support.scope_missing import ScopeMissing

PROJECT = 0
SYSTEM = Origin(environment=ScopeMissing.raised, actor=Actor.system(), role=AgentRole.MAIN)


class Scope:
    """The origin of this thread of work, its environment, actor, role and agent, which every scoped read and write is in: set where a request, a hook or a command enters, cleared when it ends."""

    def __init__(self, environments: Environments) -> None:
        self.environments = environments

    @property
    def origin(self) -> Origin:
        return CURRENT.get(SYSTEM)

    @property
    def id(self) -> int:
        return self.origin.environment()

    @property
    def actor(self) -> Actor:
        return self.origin.actor

    @property
    def role(self) -> AgentRole:
        return self.origin.role

    @property
    def agent(self) -> Agent:
        if self.origin.agent is None:
            raise Rejection(AGENT_REQUIRED)
        return self.origin.agent

    def id_default(self, foreign: int) -> int:
        return foreign if self.origin is SYSTEM else self.origin.environment()

    def entered(self, origin: Origin) -> ScopeBinding:
        return ScopeBinding(origin)

    def environment(self, environment_id: int) -> ScopeBinding:
        return ScopeBinding(replace(self.origin, environment=lambda: environment_id))

    def requested(self, name: Callable[[], str], actor: Actor) -> ScopeBinding:
        return ScopeBinding(Origin.person_origin(cache(lambda: self.environments.entered(name())), actor))

