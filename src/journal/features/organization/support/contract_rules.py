from journal.features.organization.support.contract_problem import ContractProblem
from journal.features.organization.support.domain import Domain
from journal.features.organization.support.role import Role


class ContractRules:
    """The rules that need more than one file: Role ids are unique, a domain lists exactly the Roles in its folder, routing and edges name Roles and domains that exist, and no edge repeats; it returns every problem and holds no count or name of its own."""

    def check(self, domains: tuple[Domain, ...], roles: tuple[Role, ...], present: dict[str, frozenset[str]]) -> tuple[ContractProblem, ...]:
        return (*self.unique_roles(roles), *(problem for domain in domains for problem in self.domain(domain, present.get(domain.id, frozenset()), domains)), *(problem for role in roles for problem in self.role(role, present.get(role.domain, frozenset()))))

    def unique_roles(self, roles: tuple[Role, ...]) -> list[ContractProblem]:
        seen: dict[str, str] = {}
        problems = []
        for role in roles:
            if role.id in seen:
                problems.append(ContractProblem(self.role_path(role), "id", f"the Role id {role.id} is also used in {seen[role.id]}; Role ids are unique across domains"))
            seen.setdefault(role.id, role.domain)
        return problems

    def domain(self, domain: Domain, present: frozenset[str], domains: tuple[Domain, ...]) -> list[ContractProblem]:
        path, problems = f"domains/{domain.id}/domain.toml", []
        if not present:
            problems.append(ContractProblem(path, "roles", f"domain {domain.id} has no Role"))
        if set(domain.roles) != present or len(set(domain.roles)) != len(domain.roles):
            problems.append(ContractProblem(path, "roles", f"roles lists {', '.join(domain.roles) or 'nothing'} but the Roles in the folder are {', '.join(sorted(present)) or 'none'}; make them the same, each once"))
        for rule in domain.routing:
            problems += [ContractProblem(path, "routing", f"routing names {name}, which is not a Role of {domain.id}") for name in (rule.role, *rule.then) if name not in present]
        known = {other.id for other in domains}
        problems += [ContractProblem(path, "edge", f"edge to {edge.to}, which is not another domain") for edge in domain.edges if edge.to not in known or edge.to == domain.id]
        problems += self.repeats(path, domain.edges)
        return problems

    def role(self, role: Role, present: frozenset[str]) -> list[ContractProblem]:
        path = self.role_path(role)
        problems = [ContractProblem(path, "edge", f"edge to {edge.to}, which is not another Role of {role.domain}") for edge in role.edges if edge.to not in present or edge.to == role.id]
        return problems + self.repeats(path, role.edges)

    @staticmethod
    def repeats(path: str, edges: tuple) -> list[ContractProblem]:
        pairs = [(edge.kind, edge.to) for edge in edges]
        return [ContractProblem(path, "edge", f"the edge {kind} to {to} is listed twice") for kind, to in dict.fromkeys(pair for pair in pairs if pairs.count(pair) > 1)]

    @staticmethod
    def role_path(role: Role) -> str:
        return f"domains/{role.domain}/roles/{role.id}/role.toml"
