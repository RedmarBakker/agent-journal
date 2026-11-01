from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_without_domain_seats import TASK_BRIEF
from tests.stories.fixtures.main.organization_shared_role_domain_seat_started import OrganizationSharedRoleDomainSeatStarted


@story(OrganizationSharedRoleDomainSeatStarted, subject=AgentRole.MAIN)
def test_a_domain_handoff_creates_the_shared_role_rig_and_delivers_its_job(story):
    plan, task = story.plans.first, story.tasks.first
    domain = story.organization_seat_agent("domain:alpha")
    inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()

    handed = story.agent_runs_from_openrig_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/shared",
    )
    handed.expect_command_passed()
    worker = story.newest("workers")
    story.fixture.workers.first = worker
    role = story.agents.workers.first()
    story.expect_worker_role_job(role, task, TASK_BRIEF, "the earlier task brief")
    story.expect_role_job_prompt(role, TASK_BRIEF, "the earlier task brief", "journal clock-in")
    started = story.agent_starts_role_session(role)
    started.expect_allowed(role)
    story.expect_openrig_seat_environment(role, "role:alpha/shared")
    clocked_in = story.agent_clocks_in(role)
    clocked_in.expect_command_passed()
    story.agent_reads(role).expect_allowed()

    from journal.features.organization.support.seat_runtime import SeatRuntime

    plan_rig = story.plan_rig_name(plan)
    plan_target = SeatRuntime.target(plan_rig, "plan", "plan-agent")
    story.simulated_seats().sessions[plan_target].update(pid=2_147_483_647, lifecycle="det")
    plan_status = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"plan show {plan}",
    )
    plan_status.expect_command_passed()
    plan_status.expect_command_text(f"Plan agent: environment plan-{plan}, running")
    story.expect_task(task, state=TaskState.STARTED, delegated=True)
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_organization_handoff_pending(plan, task, "role:alpha/shared")
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan)


@story(OrganizationSharedRoleDomainSeatStarted, subject=AgentRole.MAIN)
def test_a_domain_handoff_starts_a_shared_read_only_role_for_its_inbox(story):
    plan, task = story.plans.first, story.tasks.first
    domain = story.organization_seat_agent("domain:alpha")
    result = story.agent_runs_from_openrig_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/security-owner",
    )
    result.expect_command_passed()

    role = story.organization_seat_agent("role:alpha/security-owner")
    started = story.agent_starts_organization_seat(role, "role:alpha/security-owner")
    started.expect_allowed(role)
    story.expect_openrig_seat_environment(role, "role:alpha/security-owner")
    inbox = story.agent_runs_from_openrig_organization_seat(role, "role:alpha/security-owner", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")
    inbox.expect_command_text(TASK_BRIEF)

    plan_status = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"plan show {plan}",
    )
    plan_status.expect_command_passed()
    plan_status.expect_command_text(f"Plan agent: environment plan-{plan}, running")
    story.expect_row_count("workers", 0)
    story.expect_organization_handoff_pending(plan, task, "role:alpha/security-owner")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan)


@story(OrganizationSharedRoleDomainSeatStarted, subject=AgentRole.MAIN)
def test_a_failed_shared_role_start_leaves_no_handoff_row(story):
    plan, task = story.plans.first, story.tasks.first
    reason = "shared Role needs operator attention"
    story.simulated_seats().next_attention_reason = reason
    domain = story.organization_seat_agent("domain:alpha")
    result = story.agent_runs_from_openrig_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/security-owner",
    )
    result.expect_command_refused()
    result.expect_command_text(f"needs attention: {reason}")

    story.expect_organization_handoff_count(plan, 1)
    story.expect_task(task, state=TaskState.OPEN, delegated=False)
    story.expect_row_count("workers", 0)
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan)
