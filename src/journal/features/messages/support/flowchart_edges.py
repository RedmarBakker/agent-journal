import re

from journal.support.rejection import Rejection


class FlowchartEdges:
    """The arrows of a flowchart as the agent writes them: `From -> To`, or `From -> To: the words on the arrow`."""

    ARROW = re.compile(r"\s*([^:]+?)\s*->\s*([^:]+?)\s*(?::\s*(.*?))?\s*")

    @classmethod
    def read(cls, lines: list[str]) -> list[list[str]]:
        if not lines:
            raise Rejection("a flowchart needs at least one arrow: --edge 'From -> To'")
        return [cls.arrow(line) for line in lines]

    @classmethod
    def arrow(cls, line: str) -> list[str]:
        match = cls.ARROW.fullmatch(line)
        if match is None:
            raise Rejection(f"'{line}' is not an arrow: write it as 'From -> To' or 'From -> To: label'")
        return list(match.groups(default=""))
