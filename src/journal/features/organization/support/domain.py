from dataclasses import dataclass

from journal.features.organization.support.board_phases import BoardPhases
from journal.features.organization.support.edge import Edge
from journal.features.organization.support.role_models import RoleModels
from journal.features.organization.support.routing_rule import RoutingRule


@dataclass(frozen=True)
class Domain:
    """One domain read from its contract: what it stands for, the icon the sidebar shows, the names of its board's phases, the Roles its Domain agent leads, its edges to other domains and the guidance its Roles share."""

    id: str
    title: str
    icon: str
    description: str
    outcome: str
    responsible: tuple[str, ...]
    not_responsible: tuple[str, ...]
    roles: tuple[str, ...]
    skills: tuple[str, ...]
    models: RoleModels
    guidance: str
    edges: tuple[Edge, ...]
    routing: tuple[RoutingRule, ...]
    board: BoardPhases = BoardPhases()

    def has_role(self, role_id: str) -> bool:
        return role_id in self.roles
