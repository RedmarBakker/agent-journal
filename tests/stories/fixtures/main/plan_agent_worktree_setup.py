from journal.features.plans.plans_options import PlansOptions
from tests.stories.builder.plan_agent_worktree import prepare_plan_agent_worktrees
from tests.stories.fixtures.main.new_session import NewSession


class PlanAgentWorktreeSetup(NewSession):
    """The main agent has enabled Plan agents and the project has a Git worktree setup."""

    settings = ((PlansOptions.PLAN_AGENTS, True),)

    def steps(self, story) -> None:
        prepare_plan_agent_worktrees(story, story.monkeypatch)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main)
