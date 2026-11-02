from journal.engine.states.ended import Ended
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.paused_organization_plan_with_old_agent_row import PausedOrganizationPlanWithOldAgentRow


@story(PausedOrganizationPlanWithOldAgentRow, subject=AgentRole.MAIN)
def test_a_restarted_plan_revives_its_ended_agent_and_delivers_its_message(story):
    plan, task = story.plans.first, story.tasks.first
    started = story.user_starts_plan(plan)
    started.expect_viewer_passed()
    started.expect_agent_not_told(story.agents.main, PlansNudges.PLAN_STALLED, n=plan)

    seat = story.agent_starts_plan_seat(story.agents.main, plan)
    seat.expect_allowed()
    plan_agent = story.organization_seat_agent_in_plan("plan", plan)
    story.expect_row_count_in(f"plan-{plan}", "agents", 2)
    story.expect_agent_session_in_environment(plan_agent, f"plan-{plan}")
    story.expect_state_data(plan_agent, LeadingPlan, plan_id=plan)
    story.expect_stack(StoryAgent(AgentRole.MAIN, session="old-plan-agent-session"), CoordinatingPlans, Ended)

    text = "continue with the engineering task"
    told = story.agent_runs(plan_agent, f"plan tell {plan} '{text}'")
    told.expect_command_passed()
    story.expect_message_text_in_environment(f"plan-{plan}", text)

    handoff = story.agent_runs_from_plan_organization_seat(
        plan_agent, "plan", f"organization handoff {task} domain:alpha",
    )
    handoff.expect_command_passed()
    handoff.expect_command_text(f"task {task} routed from plan to domain:alpha")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_organization_handoff_pending(plan, task, "domain:alpha")
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
