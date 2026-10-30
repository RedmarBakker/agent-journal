from dataclasses import dataclass, field

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class TaskOutcome(Scoped):
    """One immutable execution, wait, resource or delivery fact for a task."""

    kind: str = ""
    event_key: str = ""
    task_id: int = 0
    plan_id: int = 0
    domain_name: str = ""
    policy_version: str = ""
    occurred_at: float = 0.0
    planning_baseline_size: int | None = None
    planned_size: int | None = None
    first_ready_size: int | None = None
    committed_size: int | None = None
    final_size: int | None = None
    scope_added: bool | None = None
    delivery_generation: int = 0
    agent_session: str = ""
    details: dict = field(default_factory=dict)
