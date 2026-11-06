from datetime import datetime, timezone

from tests.stories.fixtures.supervisor.supervisor_scheduled_wake import SupervisorScheduledWake


class SupervisorQuietWakes(SupervisorScheduledWake):
    """Scheduled wake history starts just before midnight UTC."""

    story_start_at = datetime(2026, 11, 6, 23, 46, tzinfo=timezone.utc).timestamp()
