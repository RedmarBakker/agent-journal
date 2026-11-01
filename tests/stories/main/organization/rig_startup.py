import json

from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_seat import OrganizationPlanSeat
from tests.stories.fixtures.main.organization_plan_with_missing_domain_identity import OrganizationPlanWithMissingDomainIdentity


@story(OrganizationPlanSeat, subject=AgentRole.MAIN)
def test_a_generated_plan_seat_starts_without_project_mcp_attention(story):
    project_mcp = story.app.config.root / ".mcp.json"
    project_mcp.write_text(json.dumps({"mcpServers": {"exa": {}, "context7": {}}}))
    plan, task = story.plans.first, story.tasks.first
    started = story.user_starts_plan(plan)
    started.expect_viewer_passed()
    story.expect_openrig_no_attention(story.plan_rig_name(plan))

    handoff = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    handoff.expect_command_passed()
    story.expect_organization_handoff_pending(plan, task, "domain:alpha")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_plan_rig(plan, story.plan_rig_name(plan))
    story.expect_stack(story.agents.main, CoordinatingPlans)


@story(OrganizationPlanSeat, subject=AgentRole.MAIN)
def test_a_partial_organization_rig_start_is_linked_and_reports_its_attention(story):
    plan, task = story.plans.first, story.tasks.first
    reason = "Claude needs approval for a project MCP server"
    story.simulated_seats().next_attention_reason = reason

    started = story.agent_runs(story.agents.main, f"plan start {plan}")
    started.expect_command_passed()
    story.expect_recent_message_text(f"Plan {plan} needs OpenRig attention: OpenRig rig {story.plan_rig_name(plan)} needs attention: {reason}")
    story.expect_openrig_attention(story.plan_rig_name(plan), reason)
    story.expect_plan_rig(plan, story.plan_rig_name(plan))
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_stack(story.agents.main, CoordinatingPlans)


@story(OrganizationPlanWithMissingDomainIdentity, subject=AgentRole.MAIN)
def test_a_refused_domain_handoff_does_not_write_an_inbox_row(story):
    plan, task = story.plans.first, story.tasks.first
    refused = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    refused.expect_command_refused()
    refused.expect_command_text(f"OpenRig rig {story.plan_rig_name(plan)} has no organization seat domain:alpha")
    story.expect_organization_handoff_count(plan, 0)
    story.expect_task(task, state=TaskState.OPEN, delegated=False)
    story.expect_stack(story.agents.main, CoordinatingPlans)
