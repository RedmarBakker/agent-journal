from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.paused_organization_hub_plan import PausedOrganizationHubPlan


@story(PausedOrganizationHubPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_restarted_plan_refreshes_its_seat_settings_and_keeps_its_rig(story):
    plan = story.plans.first
    rig = f"plan-{plan}"
    result = story.agent_runs(story.agents.main, f"plan start {plan}")
    result.expect_command_passed()
    seat = story.agent_runs_from_openrig_organization_seat(story.agents.main, "plan", f"organization handoff {story.tasks.first} domain:alpha")
    seat.expect_command_passed()
    seat.expect_command_text(f"task {story.tasks.first} routed from plan to domain:alpha")
    story.expect_task_tied_to_domain(story.tasks.first, "alpha")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_plan_rig(plan, rig)
    story.expect_plan_seat_settings(rig)
    story.expect_runtime_file(f"rigs/{rig}/saved-conversation.json", "previous conversation")
    story.expect_stack(story.agents.main, CoordinatingPlans, OrchestratingPlan)
