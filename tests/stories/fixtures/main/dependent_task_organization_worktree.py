from datetime import datetime, timezone

from journal.engine.clock import Clock
from journal.support.time_source import TimeSource
from tests.stories.fixtures.main.organization_plan_agent_worktree_project import OrganizationPlanAgentWorktreeProject


class DependentTaskOrganizationWorktree(OrganizationPlanAgentWorktreeProject):
    """The dependent-task organization story starts at a fixed UTC time."""

    parent = OrganizationPlanAgentWorktreeProject
    story_start_at = datetime(2026, 11, 6, 23, 46, tzinfo=timezone.utc).timestamp()

    def restore_on(self, story) -> None:
        super().restore_on(story)
        story.app.container.get(TimeSource).pin(self.story_start_at)
        story.app.container.get(Clock).held_at = self.story_start_at

    def steps(self, story) -> None:
        self.restore_on(story)
