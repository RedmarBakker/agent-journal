from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_domain_role_task import OrganizationDomainRoleTask


@story(OrganizationDomainRoleTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_role_returns_completed_work_by_proving_and_clocking_out(story):
    task = story.tasks.second
    routed = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    routed.expect_command_passed()
    story.fixture.workers.first = story.newest("workers")
    worker = story.agents.workers.first()
    story.agent_starts_role_session(worker).expect_allowed(worker)
    clocked_in = story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in")
    clocked_in.expect_command_passed()

    story.agent_proves(worker, 1, "the current task brief is met: task 6 has its current brief")
    clocked_out = story.agent_clocks_out(worker, "task 6 is complete")
    clocked_out.expect_command_passed()
    checked = story.agent_runs_from_organization_seat(story.agents.main, "domain:alpha", f"worker check {worker} 1")
    checked.expect_command_passed()
    handed_back = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} plan",
    )
    handed_back.expect_command_passed()
    story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "organization inbox").expect_command_passed()
    merged = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"worker merge {worker}")
    merged.expect_command_passed()

    story.expect_task(task, state=TaskState.COMPLETED)
    story.expect_worker(worker, state=WorkerState.MERGED)
    story.expect_plan(story.plans.first, state=PlanState.FINISHED)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


@story(OrganizationDomainRoleTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_role_handoff_before_clock_out_is_refused_with_proof_and_clock_out(story):
    task = story.tasks.second
    routed = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    routed.expect_command_passed()
    story.fixture.workers.first = story.newest("workers")
    worker = story.agents.workers.first()
    story.agent_starts_role_session(worker).expect_allowed(worker)
    story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in").expect_command_passed()

    attempted = story.agent_runs_from_organization_seat(
        worker, "role:alpha/builder", f"organization handoff {task} domain:alpha",
    )
    attempted.expect_command_refused()
    attempted.expect_command_text("journal proof <point>")
    attempted.expect_command_text("journal clock-out \"<report>\"")

    story.agent_proves(worker, 1, "the current task brief is met: task 6 has its current brief")
    story.agent_clocks_out(worker, "task 6 is complete").expect_command_passed()
    checked = story.agent_runs_from_organization_seat(story.agents.main, "domain:alpha", f"worker check {worker} 1")
    checked.expect_command_passed()
    story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} plan",
    ).expect_command_passed()
    story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"worker merge {worker}").expect_command_passed()

    story.expect_task(task, state=TaskState.COMPLETED)
    story.expect_worker(worker, state=WorkerState.MERGED)
    story.expect_plan(story.plans.first, state=PlanState.FINISHED)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
