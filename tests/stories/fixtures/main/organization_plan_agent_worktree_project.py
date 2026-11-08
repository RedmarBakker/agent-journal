from datetime import datetime, timezone

from journal.engine.clock import Clock
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.ready import Ready
from journal.support.time_source import TimeSource
from tests.stories.builder.plan_agent_worktree import prepare_plan_agent_worktrees
from tests.stories.fixtures.main.organization_setup import OrganizationSetup
from tests.stories.fixtures.state_fixture import StateFixture


class OrganizationPlanAgentWorktreeProject(StateFixture):
    """The organization project has the Git setup used by Plan agent worktree stories."""

    parent = OrganizationSetup
    story_start_at = datetime(2026, 11, 6, 23, 46, tzinfo=timezone.utc).timestamp()

    def restore_on(self, story) -> None:
        super().restore_on(story)
        story.app.container.get(TimeSource).pin(self.story_start_at)
        story.app.container.get(Clock).held_at = self.story_start_at

    def steps(self, story) -> None:
        self.restore_on(story)
        prepare_plan_agent_worktrees(story, story.monkeypatch)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
