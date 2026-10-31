from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.engine.states_catalogue import StatesCatalogue
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_domain_task_with_ended_role_worker import OrganizationDomainTaskWithEndedRoleWorker


@story(OrganizationDomainTaskWithEndedRoleWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_refused_role_handoff_writes_nothing_and_preserves_the_domain_inbox(story):
    plan = story.plans.first
    task = story.tasks.first
    stale_worker = story.agents.workers.first()

    inbox = story.agent_runs_from_organization_seat(story.agents.main, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")

    refused = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    refused.expect_command_refused()
    refused.expect_command_text(f"journal worker release {stale_worker}")
    story.expect_organization_handoff_absent(plan, task, "role:alpha/builder")
    inbox_after = story.agent_runs_from_organization_seat(story.agents.main, "domain:alpha", "organization inbox")
    inbox_after.expect_command_passed()
    inbox_after.expect_command_text("no tasks handed to domain:alpha")
    story.expect_task(task, state=TaskState.OPEN, delegated=True)
    story.expect_worker(stale_worker, state=WorkerState.UNFINISHED)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


@story(OrganizationDomainTaskWithEndedRoleWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_domain_can_release_an_ended_worker_and_handoff_its_task_to_the_role(story):
    plan = story.plans.first
    task = story.tasks.first
    stale_worker = story.agents.workers.first()
    brief = "- first is done"
    old_brief = "The earlier run ended without clocking out."

    inbox = story.agent_runs_from_organization_seat(story.agents.main, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")

    other_domain = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:beta", f"worker release {stale_worker}",
    )
    other_domain.expect_command_refused()
    other_domain.expect_command_text(f"worker {stale_worker} is not assigned to a Role in domain beta")

    refused = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    refused.expect_command_refused()
    refused.expect_command_text(f"journal worker release {stale_worker}")
    released = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"worker release {stale_worker}",
    )
    released.expect_command_passed()
    released.expect_command_text(f"worker {stale_worker} Earlier organization writer released; its task is free again")
    story.expect_worker(stale_worker, state=WorkerState.RELEASED)
    story.expect_task(task, state=TaskState.OPEN, delegated=False)

    handed_off = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    handed_off.expect_command_passed()
    handed_off.expect_command_text(f"task {task} routed from domain:alpha to role:alpha/builder")
    new_worker = story.newest("workers")
    story.fixture.workers.second = new_worker
    role_worker = story.agents.workers.second()
    story.expect_organization_handoff_pending(plan, task, "role:alpha/builder")
    story.expect_worker_role_job(role_worker, task, brief, old_brief)
    story.expect_organization_domain_can_release_workers(f"plan-{plan}", "alpha")
    story.expect_plan(plan, state=PlanState.STARTED)
    awaiting = story.app.container.get(StatesCatalogue).restored("awaiting", {})
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan, awaiting)
