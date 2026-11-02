from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from journal.supervisor_link import SupervisorLink
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.main.plan_agent_plan_started import PlanAgentPlanStarted
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION, SoloPlanAgentStarted


@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_a_main_agent_does_not_take_a_plan_task_while_its_plan_agent_runs(story):
    story.agent_stops(story.agents.main)

    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task_unheld(story.tasks.first)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)


@story(PlanAgentPlanStarted, subject=AgentRole.MAIN)
def test_a_main_agent_does_not_take_a_plan_task_while_its_plan_agent_launches(story):
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


@setting(TasksOptions.AUTO, True)
@story(SoloPlanAgentStarted, subject=AgentRole.MAIN)
def test_an_idle_main_session_does_not_take_a_plan_task_reopened_while_its_agent_runs(story):
    plan, task = story.plans.first, story.tasks.first
    environment = story.app.container.get(AgentEnvironments).environments.existing(f"plan-{plan}")
    story.monkeypatch.setattr(
        SupervisorLink, "runs", lambda _link, environment_id: environment_id == environment.row_id,
    )
    story.user_blocks_task(task, "the owner is waiting on a decision").expect_viewer_passed()
    story.expect_plan(plan, state=PlanState.BLOCKED)

    plan_agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
    status = story.agent_in_runs(plan_agent, f"plan-{plan}", PLAN_AGENT_SESSION, f"plan show {plan}")
    status.expect_command_passed()
    status.expect_command_text(f"Plan agent: environment plan-{plan}, running")

    idle_main = StoryAgent(AgentRole.MAIN, session="s2")
    story.second_session_starts("s2").expect_allowed(idle_main)
    story.expect_stack(idle_main, CoordinatingPlans, FollowingPlan)
    story.user_did(f"/journal/tasks/{task}/unblock", {}, "user reopens the Plan agent task").expect_viewer_passed()
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_task_unheld(task)

    story.agent_stops(idle_main).expect_allowed(idle_main)
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_task_unheld(task)
    story.expect_stack(idle_main, CoordinatingPlans, FollowingPlan)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)
