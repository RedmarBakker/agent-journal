from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.main.solo_plan_agent_started import SoloPlanAgentStarted


@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_a_main_agent_does_not_take_a_plan_task_while_its_plan_agent_runs(story):
    story.agent_stops(story.agents.main)

    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task_unheld(story.tasks.first)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)


@setting(PlansOptions.PLAN_AGENTS, True)
@story(PlanApproved, subject=AgentRole.MAIN)
def test_a_main_agent_does_not_take_a_plan_task_while_its_plan_agent_launches(story):
    story.monkeypatch.setattr(AgentEnvironments, "launched", lambda places, environment, agent, repositories=None: None)
    result = story.agent_runs(story.agents.main, f"plan start {story.plans.first}")
    result.expect_command_passed()

    story.agent_stops(story.agents.main)

    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task_unheld(story.tasks.first)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)


@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_a_main_agent_cannot_start_a_plan_agents_task(story):
    result = story.agent_runs(story.agents.main, f"task start {story.tasks.first}")

    result.expect_command_refused()
    result.expect_command_text("Plan agent")
    result.expect_command_text(f"for plan {story.plans.first}")
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task_unheld(story.tasks.first)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)


@setting(PlansOptions.PLAN_AGENTS, True)
@story(PlanApproved, subject=AgentRole.MAIN)
def test_a_main_agent_cannot_start_an_approved_plan_agents_task(story):
    result = story.agent_runs(story.agents.main, f"task start {story.tasks.first}")

    result.expect_command_refused()
    result.expect_command_text("Plan agent")
    result.expect_command_text(f"for plan {story.plans.first}")
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task_unheld(story.tasks.first)
    story.expect_stack(story.agents.subject, CoordinatingPlans)


@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_a_main_agent_cannot_complete_a_plan_agents_task(story):
    result = story.agent_runs(story.agents.main, f"task complete {story.tasks.first} --how completed")

    result.expect_command_refused()
    result.expect_command_text("Plan agent")
    result.expect_command_text(f"for plan {story.plans.first}")
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task_unheld(story.tasks.first)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)
