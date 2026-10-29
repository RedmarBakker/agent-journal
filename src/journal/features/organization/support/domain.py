from dataclasses import dataclass

from journal.features.organization.support.board_phases import BoardPhases
from journal.features.organization.support.edge import Edge
from journal.features.organization.support.role import Role
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

    def body(self) -> str:
        duties = "\n".join([Role.listed("You are responsible for", self.responsible), Role.listed("You do not", self.not_responsible), Role.listed("You lead the Roles", self.roles)])
        leadership = (f"You are the Domain agent for {self.title}. Lead your pod's Roles and never write code. "
                      "After a Role responds, return its report to the Plan agent through the same delegation.")
        routing = self.routing_guidance()
        return "\n\n".join(part for part in (self.guidance.strip(), leadership, duties, routing) if part)

    def routing_guidance(self) -> str:
        if not self.routing:
            return ""
        rules = []
        for rule in self.routing:
            follow = ""
            if rule.then:
                roles = " then ".join(f"Role {role}" for role in rule.then)
                follow = f"; for a real handoff, review, or approval, continue to {roles}"
            rules.append(f"- For {rule.when}, start with Role {rule.role}{follow}.")
        return "Routing from domain.toml:\n" + "\n".join(rules)
