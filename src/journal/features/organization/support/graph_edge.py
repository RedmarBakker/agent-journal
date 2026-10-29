from dataclasses import dataclass

from journal.features.organization.support.edge_kind import EdgeKind


@dataclass(frozen=True)
class GraphEdge:
    """An edge of the organization's graph between two qualified ids, plan, domain:<id> or role:<domain>/<id>; declared is false for an edge containment gives."""

    source: str
    kind: EdgeKind
    target: str
    about: str
    declared: bool
