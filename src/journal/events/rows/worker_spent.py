from dataclasses import dataclass
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.row_event import RowEvent
from journal.models.model_tier import ModelTier


@dataclass(frozen=True, kw_only=True)
class WorkerSpent(RowEvent):
    """A worker's run ended and its cost was added: the model it ran on and that model's tier, the tier of its profile's own model, and its spend in dollars before the run and after it."""

    worker: WorkerMention
    model: str
    tier: ModelTier
    profile_tier: ModelTier
    before_dollars: float
    cost_dollars: float

    def is_shaped_work_on_strongest(self) -> bool:
        return self.tier == ModelTier.STRONGEST and self.profile_tier in (ModelTier.FAST, ModelTier.GENERAL)

    def crossed(self, limit: float) -> bool:
        return self.before_dollars < limit <= self.cost_dollars
