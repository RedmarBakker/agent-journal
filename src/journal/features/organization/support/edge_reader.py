from journal.features.organization.support.edge import Edge
from journal.features.organization.support.edge_kind import EdgeKind
from journal.features.organization.support.toml_fields import TomlFields


class EdgeReader:
    """Reads the [[edges]] of a contract: each has one of the five kinds, a target and what passes along it; whether the target exists is for the rules across files."""

    def read(self, fields: TomlFields) -> tuple[Edge, ...]:
        edges = []
        for table in fields.tables("edges"):
            kind, to, about = table.text("kind"), table.text("to"), table.text("about")
            table.unknown(("kind", "to", "about"))
            fields.absorbed(table)
            if kind and kind not in EdgeKind:
                fields.problem("edge", f"edge kind {kind} is not one of {', '.join(EdgeKind)}")
            elif kind and to and about:
                edges.append(Edge(EdgeKind(kind), to, about))
        return tuple(edges)
