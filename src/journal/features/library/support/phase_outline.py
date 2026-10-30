from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseOutline:
    """One phase of a plan outline: its title, its complete-when line, whether the user looks before the plan goes on, and its tasks' titles."""

    title: str
    completion_rule: str
    checkpoint: bool
    task_titles: tuple[str, ...]
