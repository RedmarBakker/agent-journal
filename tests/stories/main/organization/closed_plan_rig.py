from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.repositories.plans import Plans
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_shared_role_domain_inbox_read import OrganizationSharedRoleDomainInboxRead


@story(OrganizationSharedRoleDomainInboxRead, subject=AgentRole.MAIN)
def test_a_closed_plan_keeps_a_shared_rig_used_by_another_live_plan(story):
    first_plan = story.plans.first
    second_plan = story.user_creates_plan("Second organization plan", "Keep the shared Role in use")
    second_task = story.user_adds_plan_task(second_plan, "Second task", "alpha")
    story.user_presses(f"/journal/plans/{second_plan}/mode", {"mode": "organization"}).expect_viewer_passed()
    story.user_approves_plan(second_plan).expect_viewer_passed()
    story.user_starts_plan(second_plan).expect_viewer_passed()
    second_plan_agent = story.organization_seat_agent_in_plan("plan", second_plan)
    story.agent_starts_organization_seat_in_plan(second_plan_agent, "plan", second_plan).expect_allowed(second_plan_agent)
    second_domain_handoff = story.agent_runs_as_organization_seat_in_plan(
        second_plan_agent, "plan", second_plan,
        f"organization handoff {second_task} domain:alpha",
    )
    second_domain_handoff.expect_command_passed()
    second_domain = story.organization_seat_agent_in_plan("domain:alpha", second_plan)
    story.agent_starts_organization_seat_in_plan(second_domain, "domain:alpha", second_plan).expect_allowed(second_domain)
    second_shared_handoff = story.agent_runs_as_organization_seat_in_plan(
        second_domain, "domain:alpha", second_plan,
        f"organization handoff {second_task} role:alpha/security-owner",
    )
    second_shared_handoff.expect_command_passed()
    plan_row = story.app.container.get(Plans).global_matching(id=second_plan)[0]
    shared_rig = story.app.container.get(RigStaffing).shared_rig_name(plan_row.environment_id)

    story.user_cancels_plan(first_plan).expect_viewer_passed()
    story.settle()

    story.expect_plan(first_plan, state=PlanState.CANCELLED)
    story.expect_plan(second_plan, state=PlanState.STARTED)
    story.expect_openrig_rig_stopped(story.plan_rig_name(first_plan))
    story.expect_openrig_rig_running(shared_rig)
    story.expect_stack(second_domain, LeadingPlan, FollowingPlan)
