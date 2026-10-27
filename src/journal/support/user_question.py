from dataclasses import dataclass

from journal.support.operation import Operation


@dataclass(frozen=True)
class UserQuestion(Operation):
    """A question the agent puts to the user with its program's own tool, which the viewer never sees."""

    operation_type = "user question"
