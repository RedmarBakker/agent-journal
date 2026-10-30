from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.tasks.states.ready import Ready
from journal.features.workers.organization_options import OrganizationOptions
from journal.repositories.environments import Environments
from journal.support.agent_role import AgentRole
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.builder.story_marks import BUILDER_MODE, setting, story
from tests.stories.fixtures.main.plan_approved import PlanApproved


def start_plan_agent(story):
    root, plan = story.app.config.root, story.plans.first
    story.project_is_a_git_repository()
    story.git_in(root, "config", "user.name", "Story")
    story.git_in(root, "config", "user.email", "story@example.com")
    story.monkeypatch.setattr(
        AgentEnvironments,
        "launched",
        lambda places, environment, agent, repositories=None: WorkspaceWorktree.chosen(root, environment.name, repositories).created(),
    )
    result = story.agent_runs(story.agents.main, f"plan start {plan}")
    result.expect_command_passed()
    environment = story.app.container.get(Environments).existing(f"plan-{plan}")
    session = "plan-agent-write-session"
    story.session_starts_in(environment.name, session)
    return environment, session, WorkspaceWorktree.chosen(root, environment.name)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
@setting(OrganizationOptions.PLAN_MODE, "solo")
def test_a_plan_agent_may_write_inside_its_plan_worktree(story):
    environment, session, tree = start_plan_agent(story)
    result = story.agent_writes_in_environment(story.agents.main, environment.name, session, str(tree.path), str(tree.path / "inside.md"))
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
@setting(OrganizationOptions.PLAN_MODE, "solo")
def test_a_plan_agent_write_outside_its_worktree_is_refused(story):
    environment, session, tree = start_plan_agent(story)
    path = story.app.config.root / "outside-the-plan.md"
    result = story.agent_writes_in_environment(story.agents.main, environment.name, session, str(tree.path), str(path))
    result.expect_refused_by_anything()
    story.expect_told_in(environment.name, PlansNudges.PLAN_AGENT_WRITE_SCOPE, path=str(path), worktree=str(tree.path))
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
