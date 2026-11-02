"""Runs Git in a project with an ignored inner repository to show a solo plan's edit merged from its own worktree."""
from journal.engine.agent_launcher import AgentLauncher
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.support.agent_role import AgentRole
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.plan_approved import PlanApproved


@story(PlanApproved, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_a_solo_plan_commits_and_automatically_merges_its_inner_repository_edit(story, monkeypatch):
    root = story.app.config.root
    story.project_is_a_git_repository()
    story.git_in(root, "config", "user.name", "Story")
    story.git_in(root, "config", "user.email", "story@example.com")
    repository = root / "agentic-organization"
    repository.mkdir()
    story.git_in(repository, "init", "-q", "-b", "main")
    story.git_in(repository, "config", "user.name", "Story")
    story.git_in(repository, "config", "user.email", "story@example.com")
    story.git_in(repository, "commit", "-q", "--allow-empty", "-m", "inner start")
    (root / ".gitignore").write_text("agentic-organization/\n")
    story.git_in(root, "add", ".gitignore")
    story.git_in(root, "commit", "-q", "-m", "ignore the inner repository")
    story.user_rewrites_the_brief(story.tasks.first, "Edit agentic-organization/ARCHITECTURE.md.")
    monkeypatch.setattr(AgentLauncher, "launched", lambda launcher, environment, arguments: 0)
    plan = story.plans.first
    story.agent_runs(story.agents.main, f"plan start {plan}")
    environment, session = f"plan-{plan}", "plan-inner-repository-session"
    story.session_starts_in(environment, session)
    tree = WorkspaceWorktree.chosen(root, environment)
    change = tree.path / "agentic-organization" / "ARCHITECTURE.md"
    change.write_text("edited in the Plan agent worktree\n")
    story.git_in(change.parent, "add", change.name)
    story.git_in(change.parent, "commit", "-q", "-m", "edit the architecture")
    story.agent_in_runs(story.agents.main, environment, session, f"task complete {story.tasks.first} --how done")
    story.agent_in_runs(story.agents.main, environment, session, f"task complete {story.tasks.second} --how done")
    story.expect_project_file_is("agentic-organization/ARCHITECTURE.md", "edited in the Plan agent worktree\n")
    story.expect_no_project_file(".claude/worktrees/plan-1/agentic-organization")
    story.expect_no_project_file(f".claude/worktrees/{environment}")
    story.expect_stack(story.agents.main, CoordinatingPlans)
