from journal.engine.demand import Demand
from journal.events.feature_data import FeatureData
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.plans_part import PlansPart
from journal.support.timeout import Timeout

# the tool uses before the hold during which the review demand says nothing past its first request
REVIEW_SILENT_USES = 3


def reviewed(data: FeatureData) -> int | None:
    return data.part(PlansPart).review_plan or None


class PlansDemands:
    """What the plans feature demands of the agent: a plan whose reviewers are all back is written into and readied before its span runs out; its writes are then refused."""

    REVIEW_ENTRY = Demand(
        key="plans.review_entry",
        requirement=reviewed,
        line=lambda plan, balance: PlansNudges.review_countdown(plan, balance),
        refusal=lambda plan: PlansNudges.REVIEW_ENTRY_BLOCK.create(n=plan),
        exemption=lambda event, plan: False,
        span=lambda settings: Timeout.tool_uses(settings.integer(PlansOptions.REVIEW_TOOL_USE_LIMIT)),
        block_scope=lambda event: bool(event.call.writes),
        silence=lambda settings: Timeout.tool_uses(max(settings.integer(PlansOptions.REVIEW_TOOL_USE_LIMIT) - REVIEW_SILENT_USES, 0)),
    )
