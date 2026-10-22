from dataclasses import dataclass

from journal.support.operation import Operation


@dataclass(frozen=True)
class SubagentDispatch(Operation):
    """The agent starting one of its program's own subagents: the profile and the model it names, its short title, its brief, and whether it runs in the background while the agent continues; a profile, a model or a brief the program's tool cannot provide is None."""

    kind = "subagent dispatch"
    role: str | None
    model: str | None
    title: str
    brief: str | None
    background: bool
