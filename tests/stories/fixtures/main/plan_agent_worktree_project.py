from tests.stories.builder.plan_agent_worktree import prepare_plan_agent_worktrees
from tests.stories.fixtures.main.new_session import NewSession


class PlanAgentWorktreeProject(NewSession):
    """The project has the Git setup used by Plan agent worktree stories."""

    def steps(self, story) -> None:
        prepare_plan_agent_worktrees(story, story.monkeypatch)
