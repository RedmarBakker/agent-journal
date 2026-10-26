from journal.features.workers.support.line_bands import LineBands


class OpposedLines:
    """The pairs of lines that ask the agent opposite things, one to hand out more and one to hand out less, read from the band table."""

    @classmethod
    def opposed(cls, first: str, second: str) -> bool:
        pairs = LineBands.opposed_pairs()
        return (first, second) in pairs or (second, first) in pairs
