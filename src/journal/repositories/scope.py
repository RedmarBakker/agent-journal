from dataclasses import replace
from functools import cache
from typing import Callable

from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.models.support.ref import Ref
from journal.repositories.environments import Environments
from journal.repositories.links import Links
from journal.repositories.origin import Origin
from journal.repositories.scope_binding import CURRENT, ScopeBinding
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.support.caller import AGENT_REQUIRED
from journal.support.rejection import Rejection
from journal.support.scope_missing import ScopeMissing

PROJECT = 0
BOUND_LINK = "bound_to"
SYSTEM = Origin(environment=ScopeMissing.raised, actor=Actor.system(), role=AgentRole.MAIN)


class Scope:
    """The origin of this thread of work, its environment, actor, role and agent, which every scoped read and write is in: set where a request, a hook or a command enters, cleared when it ends; a hub row bound to it by a bound_to link is its work as well."""

    def __init__(self, environments: Environments, links: Links) -> None:
        self.environments, self.links = environments, links

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

    def bound(self) -> tuple[Ref, ...]:
        environment = Ref(Environment.table(), self.id)
        return tuple(link.source for link in self.links.unlisted_kind_links(BOUND_LINK) if link.target == environment)

    def binders(self, ref: Ref, member_links: tuple[str, ...]) -> tuple[int, ...]:
        bindings = self.links.unlisted_kind_links(BOUND_LINK)
        if not bindings:
            return ()
        owners = {ref, *(link.target for type_name in member_links for link in self.links.ref_links("source", [ref], type_name))}
        return tuple(dict.fromkeys(link.target.id for link in bindings if link.source in owners))
