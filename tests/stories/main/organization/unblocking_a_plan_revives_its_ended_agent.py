from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.agent import ENDED_STATE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.support.agent_role import AgentRole
from tests.stories.builder.main_session import MAIN_SESSION
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.blocked_organization_plan_with_old_agent_row import BlockedOrganizationPlanWithOldAgentRow, NEW_PLAN_SESSION


@story(BlockedOrganizationPlanWithOldAgentRow, subject=AgentRole.MAIN)
def test_unblocking_and_restarting_a_plan_revives_its_ended_agent(story):
    plan, task = story.plans.first, story.tasks.first
    owner = StoryAgent(AgentRole.MAIN, session=MAIN_SESSION)
    unblocked = story.agent_runs(owner, f"plan unblock {plan}")
    unblocked.expect_command_passed()
    story.expect_plan(plan, state=PlanState.STARTED)

    started = story.agent_runs(owner, f"plan start {plan}")
    started.expect_command_passed()
    environment = story.app.container.get(Environments).existing(f"plan-{plan}")
    leftover = story.app.container.get(Agents).global_matching(environment_id=environment.row_id, session=NEW_PLAN_SESSION)[0]
    story.expect_row_in(environment.name, "agents", leftover.row_id, {"state": ENDED_STATE})
    story.session_starts_in(f"plan-{plan}", NEW_PLAN_SESSION)
    plan_agent = StoryAgent(AgentRole.MAIN, session=NEW_PLAN_SESSION)
    story.expect_stack(plan_agent, LeadingPlan)

    text = "continue with the engineering task"
    told = story.agent_runs_from_plan_organization_seat(plan_agent, "plan", f"plan tell {plan} '{text}'")
    told.expect_command_passed()
    story.expect_message_text_in_environment(f"plan-{plan}", text)

    started_task = story.agent_runs_from_plan_organization_seat(plan_agent, "plan", f"task start {task}")
    started_task.expect_command_passed()
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.STARTED)
    story.expect_stack(plan_agent, LeadingPlan, FollowingPlan)
