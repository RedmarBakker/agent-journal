from functools import cache
from typing import Callable

from journal.models.environment import Environment
from journal.models.support.ref import Ref
from journal.repositories.environments import Environments
from journal.repositories.links import Links
from journal.repositories.scope_binding import CURRENT, ScopeBinding
from journal.support.scope_missing import ScopeMissing

PROJECT = 0
BOUND_LINK = "bound_to"


class Scope:
    """The environment every scoped read and write of this thread of work is in: set where a request, a hook or a command enters, cleared when it ends; a hub row bound to it by a bound_to link is its work as well."""

    def __init__(self, environments: Environments, links: Links) -> None:
        self.environments, self.links = environments, links

    @property
    def id(self) -> int:
        environment = CURRENT.get(None)
        if environment is None:
            raise ScopeMissing()
        return environment()

    def id_default(self, foreign: int) -> int:
        environment = CURRENT.get(None)
        return foreign if environment is None else environment()

    def environment(self, environment_id: int) -> ScopeBinding:
        return ScopeBinding(lambda: environment_id)

    def requested(self, name: Callable[[], str]) -> ScopeBinding:
        return ScopeBinding(cache(lambda: self.environments.entered(name())))

    def bound(self) -> tuple[Ref, ...]:
        environment = Ref(Environment.table(), self.id)
        return tuple(link.source for link in self.links.unlisted_kind_links(BOUND_LINK) if link.target == environment)

    def binders(self, ref: Ref, member_links: tuple[str, ...]) -> tuple[int, ...]:
        bindings = self.links.unlisted_kind_links(BOUND_LINK)
        if not bindings:
            return ()
        owners = {ref, *(link.target for kind in member_links for link in self.links.ref_links("source", [ref], kind))}
        return tuple(dict.fromkeys(link.target.id for link in bindings if link.source in owners))
