from dataclasses import dataclass

from journal.support.operation import Operation


@dataclass(frozen=True)
class UndecodedTool(Operation):
    """A tool the provider decodes into no operation of the journal's: it writes nothing the journal can see."""

    operation_type = "undecoded tool"
    name: str
