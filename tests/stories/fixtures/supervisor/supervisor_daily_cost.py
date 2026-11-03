from datetime import datetime, timezone

from journal.features.supervisor.support.admissions import supervisor_run_reservation_microusd
from tests.stories.fixtures.supervisor.supervisor_scheduled_wake import SupervisorScheduledWake


class SupervisorDailyCost(SupervisorScheduledWake):
    """A supervisor grant starts near the end of a UTC day with one run's cost as its cap."""

    max_input_tokens_per_turn = 1_000
    max_output_tokens_per_turn = 1_000
    daily_cost_limit_microusd = supervisor_run_reservation_microusd(
        max_input_tokens_per_turn, max_output_tokens_per_turn,
    )
    story_start_at = datetime(2026, 11, 3, 23, 45, tzinfo=timezone.utc).timestamp()
    owner_route = "/journal/supervisor/costs"
