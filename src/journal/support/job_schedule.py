from dataclasses import dataclass

from journal.support.operation import Operation


@dataclass(frozen=True)
class JobSchedule(Operation):
    """The agent scheduling a prompt of its own with its program's own tool: the cron schedule, the prompt, and whether it repeats."""

    kind = "job schedule"
    cron: str
    prompt: str
    recurring: bool
