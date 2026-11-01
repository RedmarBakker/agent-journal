from tests.stories.fixtures.main.organization_setup import OrganizationSetup
from tests.stories.fixtures.main.plan_agent_worktree_setup import PlanAgentWorktreeSetup


class OrganizationPlanAgentWorktree(PlanAgentWorktreeSetup):
    """The organization setup is ready for Plan agents to work in Git worktrees."""

    parent = OrganizationSetup
