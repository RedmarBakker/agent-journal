from dataclasses import dataclass

from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.contract_problem import ContractProblem
from journal.features.organization.support.domain import Domain
from journal.features.organization.support.edge_kind import EdgeKind
from journal.features.organization.support.graph_edge import GraphEdge
from journal.features.organization.support.role import Role

PLAN = "plan"
MAIN = "main"
CONTAINMENT = "contains"


@dataclass(frozen=True)
class Contracts:
    """Every domain and Role read from the organization folder, what was wrong in the files left out, the digest of the bytes, and the source path and commit read."""

    domains: tuple[Domain, ...]
    roles: tuple[Role, ...]
    problems: tuple[ContractProblem, ...]
    version: str
    folder: str = ""
    commit: str = ""

    def is_empty(self) -> bool:
        return not self.domains and not self.roles

    def role(self, role_id: str) -> Role | None:
        return next((role for role in self.roles if role.id == role_id), None)

    def domain(self, domain_id: str) -> Domain | None:
        return next((domain for domain in self.domains if domain.id == domain_id), None)

    def roles_of(self, domain_id: str) -> tuple[Role, ...]:
        return tuple(role for role in self.roles if role.domain == domain_id)

    def cardinality_of(self, role_id: str) -> Cardinality | None:
        role = self.role(role_id)
        return role.cardinality if role else None

    def graph(self) -> tuple[GraphEdge, ...]:
        return (*self.containment(), *self.declared())

    def containment(self) -> tuple[GraphEdge, ...]:
        edges = [GraphEdge(MAIN, EdgeKind.DELEGATES_TO, PLAN, CONTAINMENT, False), GraphEdge(PLAN, EdgeKind.ESCALATES_TO, MAIN, CONTAINMENT, False)]
        for domain in self.domains:
            edges += [GraphEdge(PLAN, EdgeKind.DELEGATES_TO, self.domain_id(domain.id), CONTAINMENT, False), GraphEdge(self.domain_id(domain.id), EdgeKind.ESCALATES_TO, PLAN, CONTAINMENT, False)]
            for role in self.roles_of(domain.id):
                edges += [GraphEdge(self.domain_id(domain.id), EdgeKind.DELEGATES_TO, self.role_id(role), CONTAINMENT, False), GraphEdge(self.role_id(role), EdgeKind.ESCALATES_TO, self.domain_id(domain.id), CONTAINMENT, False)]
        return tuple(edges)

    def declared(self) -> tuple[GraphEdge, ...]:
        roles = [GraphEdge(self.role_id(role), edge.kind, f"role:{role.domain}/{edge.to}", edge.about, True) for role in self.roles for edge in role.edges]
        domains = [GraphEdge(self.domain_id(domain.id), edge.kind, self.domain_id(edge.to), edge.about, True) for domain in self.domains for edge in domain.edges]
        return (*roles, *domains)

    @staticmethod
    def domain_id(domain_id: str) -> str:
        return f"domain:{domain_id}"

    @staticmethod
    def role_id(role: Role) -> str:
        return f"role:{role.domain}/{role.id}"
