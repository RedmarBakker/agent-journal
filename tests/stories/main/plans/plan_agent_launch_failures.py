from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from journal.support.worktree_failure import WorktreeFailure
from journal.supervisor_link import SupervisorLink
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_agent_plan_started import PlanAgentPlanStarted


@story(PlanAgentPlanStarted, subject=AgentRole.MAIN)
def test_a_failed_plan_agent_launch_is_reported_and_can_be_retried(story):
    running = set()
    attempts = 0

    def launch(places, environment, agent, repositories=()):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise WorktreeFailure(environment.name, "permission denied while making the plan worktree")
        running.add(environment.row_id)

    story.monkeypatch.setattr(AgentEnvironments, "launched", launch)
    story.monkeypatch.setattr(SupervisorLink, "runs", lambda supervisor, environment_id: environment_id in running)

    plan = story.plans.first
    result = story.agent_runs(story.agents.subject, f"plan start {plan}")
    result.expect_command_passed()
    result.expect_command_text("Plan agent did not start")
    story.expect_recent_message_text(
        f"Plan {plan}'s Plan agent did not start: the worktree plan-{plan} could not be made: permission denied while making the plan worktree"
    )
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)

    result = story.agent_runs(story.agents.subject, f"plan start {plan}")
    result.expect_command_passed()
    result.expect_command_text_without("Plan agent did not start")
    result = story.agent_runs(story.agents.subject, f"plan show {plan}")
    result.expect_command_text(f"Plan agent: environment plan-{plan}, running")
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)
