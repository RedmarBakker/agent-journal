from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.paused_organization_hub_plan import PausedOrganizationHubPlan
from tests.stories.fixtures.main.stopped_organization_hub_plan import StoppedOrganizationHubPlan


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
    story.expect_plan_rig_seat_settings(rig)
    story.expect_organization_seat_routing_guidance(rig)
    story.expect_runtime_file(f"rigs/{rig}/saved-conversation.json", "previous conversation")
    story.expect_stack(story.agents.main, CoordinatingPlans, OrchestratingPlan)


@story(StoppedOrganizationHubPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_restarted_domain_routes_its_task_to_a_writing_role(story):
    plan = story.plans.first
    task = story.tasks.first
    rig = f"plan-{plan}"
    stale_brief = "- old notes for the writer"
    brief = "- the restarted Domain seat routes the current task"
    story.user_rewrites_the_brief(task, stale_brief)
    story.user_rewrites_the_brief(task, brief)

    started = story.agent_runs(story.agents.main, f"plan start {plan}")
    started.expect_command_passed()
    handed_to_domain = story.agent_runs_from_openrig_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    handed_to_domain.expect_command_passed()
    handed_to_role = story.agent_runs_from_openrig_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    handed_to_role.expect_command_passed()
    handed_to_role.expect_command_text(f"task {task} routed from domain:alpha to role:alpha/builder")

    story.fixture.workers.first = story.newest("workers")
    worker = story.agents.workers.first()
    story.expect_worker_role_job(worker, task, brief, stale_brief)
    story.expect_role_job_prompt(worker, brief, stale_brief, "journal clock-in")
    story.expect_organization_seat_routing_guidance(rig)
    story.expect_task_tied_to_domain(task, "alpha")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_plan_rig(plan, rig)
    story.expect_plan_rig_seat_settings(rig)
    story.expect_stack(story.agents.main, CoordinatingPlans, OrchestratingPlan)
