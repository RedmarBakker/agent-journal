from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.ready import Ready
from tests.stories.builder.plan_agent_worktree import prepare_plan_agent_worktrees
from tests.stories.fixtures.main.organization_setup import OrganizationSetup
from tests.stories.fixtures.state_fixture import StateFixture


class OrganizationPlanAgentWorktreeProject(StateFixture):
    """The organization project has the Git setup used by Plan agent worktree stories."""

    parent = OrganizationSetup

    def steps(self, story) -> None:
        prepare_plan_agent_worktrees(story, story.monkeypatch)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
