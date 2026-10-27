from journal.support.rejection import Rejection

ARROW = "->"
LABEL = ":"


class FlowchartEdges:
    """The arrows of a flowchart as the agent writes them: `From -> To`, or `From -> To: the words on the arrow`."""

    @classmethod
    def read(cls, lines: list[str]) -> list[list[str]]:
        if not lines:
            raise Rejection("a flowchart needs at least one arrow: --edge 'From -> To'")
        return [cls.arrow(line) for line in lines]

    @classmethod
    def arrow(cls, line: str) -> list[str]:
        source, found, rest = line.partition(ARROW)
        target, _, label = rest.partition(LABEL)
        if not found or not source.strip() or not target.strip():
            raise Rejection(f"'{line}' is not an arrow: write it as 'From -> To' or 'From -> To: label'")
        return [source.strip(), target.strip(), label.strip()]
