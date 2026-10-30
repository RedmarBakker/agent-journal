from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.support.agent_role import AgentRole
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.builder.story_marks import BUILDER_MODE, story
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION, SoloPlanAgentStarted


def plan_agent_context(story):
    plan = story.plans.first
    environment = f"plan-{plan}"
    return environment, WorkspaceWorktree.chosen(story.app.config.root, environment)


@story(SoloPlanAgentStarted, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_agent_may_write_inside_its_plan_worktree(story):
    story.expect_task(story.tasks.first)
    environment, tree = plan_agent_context(story)
    result = story.agent_writes_in_environment(story.agents.main, environment, PLAN_AGENT_SESSION, str(tree.path), str(tree.path / "inside.md"))
    result.expect_allowed()
    story.expect_stack(story.agents.subject, CoordinatingPlans, OrchestratingPlan)


@story(SoloPlanAgentStarted, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_agent_write_outside_its_worktree_is_refused(story):
    story.expect_task(story.tasks.first)
    environment, tree = plan_agent_context(story)
    path = story.app.config.root / "outside-the-plan.md"
    result = story.agent_writes_in_environment(story.agents.main, environment, PLAN_AGENT_SESSION, str(tree.path), str(path))
    result.expect_refused_by_anything()
    story.expect_told_in(environment, PlansNudges.PLAN_AGENT_WRITE_SCOPE, path=str(path), worktree=str(tree.path))
    story.expect_stack(story.agents.subject, CoordinatingPlans, OrchestratingPlan)
