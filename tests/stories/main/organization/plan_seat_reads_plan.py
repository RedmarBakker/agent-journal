from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.organization_plan_seat import OrganizationPlanSeat


@story(OrganizationPlanSeat, subject=AgentRole.MAIN)
def test_a_plan_seat_reads_its_plan_tasks_and_handoff_targets_without_an_environment_override(story):
    plan = story.plans.first
    task = story.tasks.first
    phase = story.agent_runs(story.agents.main, f"plan phase {plan} 'Build the first part' --when 'the task is complete'")
    phase.expect_command_passed()
    placed = story.agent_runs(story.agents.main, f"plan todos {plan} 1 {task}")
    placed.expect_command_passed()
    story.agent_runs(story.agents.main, f"plan start {plan}").expect_command_passed()
    story.agent_starts_plan_seat(story.agents.main, plan)

    listed = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "plan list")
    listed.expect_command_passed()
    listed.expect_command_text(f"{plan}  started  p")

    shown = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"plan show {plan}")
    shown.expect_command_passed()
    shown.expect_command_text("phase 1: Build the first part")
    shown.expect_command_text(f"{task}")
    shown.expect_command_text("first")
    shown.expect_command_text("domain:alpha")

    task_details = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"task show {task}")
    task_details.expect_command_passed()
    task_details.expect_command_text(f"task {task}: first")
    task_details.expect_command_text(f"plan {plan}: p")

    targets = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "organization list")
    targets.expect_command_passed()
    targets.expect_command_text("domain alpha")
    targets.expect_command_text("domain beta")
    story.expect_plan_seat_journal_reads_allowed(story.plan_rig_name(plan))
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
