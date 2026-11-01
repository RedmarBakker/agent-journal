from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.support.workspace_worktree import WorkspaceWorktree


def prepare_plan_agent_worktrees(story, monkeypatch) -> None:
    root = story.app.config.root
    story.project_is_a_git_repository()
    story.git_in(root, "config", "user.name", "Story")
    story.git_in(root, "config", "user.email", "story@example.com")
    monkeypatch.setattr(
        AgentEnvironments,
        "launched",
        lambda places, environment, agent, repositories=None: WorkspaceWorktree.chosen(root, environment.name, repositories).created(),
    )
