from tests.stories.fixtures.supervisor.supervisor_scheduled_wake import (
    SupervisorScheduledWake,
    scheduled_wake,
)


class SupervisorFirstScheduledWake(SupervisorScheduledWake):
    """An active supervisor has completed one scheduled wake with no change."""

    parent = SupervisorScheduledWake

    def steps(self, story) -> None:
        story.time_travel(minutes=15)
        first = scheduled_wake(story)
        first.expect_viewer_passed()
        first.expect_viewer_part(("reason",), "empty")
