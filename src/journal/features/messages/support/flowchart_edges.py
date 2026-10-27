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
        from_name, arrow_text, after_arrow = line.partition(ARROW)
        to_name, _, label_text = after_arrow.partition(LABEL)
        if not arrow_text or not from_name.strip() or not to_name.strip():
            raise Rejection(f"'{line}' is not an arrow: write it as 'From -> To' or 'From -> To: label'")
        return [from_name.strip(), to_name.strip(), label_text.strip()]
