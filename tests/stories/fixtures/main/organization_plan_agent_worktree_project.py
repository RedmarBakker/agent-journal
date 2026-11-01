from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.organization_setup import OrganizationSetup
from tests.stories.fixtures.main.plan_agent_worktree_project import PlanAgentWorktreeProject


class OrganizationPlanAgentWorktreeProject(PlanAgentWorktreeProject):
    """The organization project has the Git setup used by Plan agent worktree stories."""

    parent = OrganizationSetup

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
