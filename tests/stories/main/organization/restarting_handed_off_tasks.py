from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_domain_role_task import OrganizationDomainRoleTask
from tests.stories.fixtures.main.organization_role_worker_ended import OrganizationRoleWorkerEnded
from tests.stories.fixtures.main.shared_role_queue import awaiting_state


@story(OrganizationDomainRoleTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_restarted_plan_resends_a_read_domain_handoff_to_the_domain_seat(story):
    plan, task = story.plans.first, story.tasks.second
    domain = story.organization_seat_agent("domain:alpha")
    started = story.agent_starts_organization_seat(domain, "domain:alpha")
    started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
    old_inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
    old_inbox.expect_command_passed()
    old_inbox.expect_command_text(f"plan {plan} task {task}: task 6 current")

    story.expect_plan(plan, state=PlanState.STARTED)

    plan_seat = story.organization_seat_agent("plan")
    plan_started = story.agent_starts_plan_seat(plan_seat, plan)
    plan_started.expect_agent_told(plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha")
    handed_to_domain = story.agent_runs_from_plan_organization_seat(
        plan_seat, "plan", f"organization handoff {task} domain:alpha",
    )
    handed_to_domain.expect_command_passed()
    story.expect_organization_handoff_pending(plan, task, "domain:alpha")

    domain_started = story.agent_starts_organization_seat(domain, "domain:alpha")
    domain_started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
    inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: task 6 current")
    role_handoff = story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    role_handoff.expect_command_passed()
    worker_number = story.newest("workers")
    story.fixture.workers.first = worker_number
    worker = story.agents.workers.first()
    story.expect_worker_role_job(worker, task, "- task 6 has its current brief", "- first is done")
    story.expect_worker(worker, state=WorkerState.DISPATCHED)
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_stack(plan_seat, LeadingPlan, FollowingPlan)


@story(OrganizationRoleWorkerEnded, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_restarted_plan_resends_an_ended_role_task_to_its_domain_seat(story):
    plan, task = story.plans.first, story.tasks.second
    ended_worker = story.agents.workers.first()
    domain = story.organization_seat_agent("domain:alpha")
    started = story.agent_starts_organization_seat(domain, "domain:alpha")
    started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
    old_inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
    old_inbox.expect_command_passed()
    old_inbox.expect_command_text(f"plan {plan} task {task}: task 6 current")
    old_inbox.expect_command_text(f"worker {ended_worker} holds this task")

    story.expect_plan(plan, state=PlanState.STARTED)

    plan_seat = story.organization_seat_agent("plan")
    plan_started = story.agent_starts_plan_seat(plan_seat, plan)
    plan_started.expect_agent_told(plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha")
    handed_to_domain = story.agent_runs_from_plan_organization_seat(
        plan_seat, "plan", f"organization handoff {task} domain:alpha",
    )
    handed_to_domain.expect_command_passed()
    story.expect_organization_handoff_pending(plan, task, "domain:alpha")

    domain_started = story.agent_starts_organization_seat(domain, "domain:alpha")
    domain_started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
    inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: task 6 current")
    inbox.expect_command_text(f"worker {ended_worker} holds this task")

    story.expect_worker(ended_worker, state=WorkerState.UNFINISHED)
    story.expect_stack(plan_seat, LeadingPlan, FollowingPlan, awaiting_state(story))
