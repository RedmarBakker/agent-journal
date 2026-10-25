from typing import ClassVar

from journal.db.migration import Migration


class PlanApprovalChoice(Migration):
    """The orchestrator's switch to approve only the plans it did not write becomes the choice of the plans it may approve: on is the plans the user made, off leaves the choice at its default, all plans."""

    number: ClassVar[int] = 55
    statements: ClassVar[tuple[str, ...]] = (
        "INSERT INTO settings (created_at, creator, updated_at, updater, environment_id, key, value) "
        "SELECT created_at, creator, updated_at, updater, environment_id, 'workers.orchestrator_plan_approval', '\"can approve plans the user made\"' "
        "FROM settings WHERE key = 'workers.orchestrator_approves_others_plans' AND value = 'true' "
        "AND NOT EXISTS (SELECT 1 FROM settings AS chosen WHERE chosen.environment_id = settings.environment_id AND chosen.key = 'workers.orchestrator_plan_approval')",
        "DELETE FROM settings WHERE key = 'workers.orchestrator_approves_others_plans'",
    )
