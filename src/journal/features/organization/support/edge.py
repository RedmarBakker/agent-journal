from dataclasses import dataclass

from journal.features.organization.support.edge_kind import EdgeKind


@dataclass(frozen=True)
class Edge:
    """An edge from the Role or domain that declares it to another Role of its domain, or another domain, and what passes along it."""

    kind: EdgeKind
    to: str
    about: str

    def is_kind(self, kind: EdgeKind) -> bool:
        return self.kind == kind
