from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_task_split_domain_read import OrganizationTaskSplitDomainRead
from tests.stories.fixtures.main.shared_role_queue import awaiting_state

MULTI_POINT_BRIEF = "- the first point is met\n- the second point is met"


@story(OrganizationTaskSplitDomainRead, subject=AgentRole.MAIN)
def test_a_domain_checks_unchecked_role_proofs_before_returning_parts_to_the_plan(story):
    plan, parent = story.plans.first, story.tasks.first
    domain = story.organization_seat_agent("domain:alpha")

    first_started = story.agent_runs_as_organization_seat(
        domain, "domain:alpha",
        f'organization part {parent} role:alpha/builder "first part" --brief "{MULTI_POINT_BRIEF}"',
    )
    first_started.expect_command_passed()
    first_part = story.newest("tasks")
    story.fixture.workers.__setattr__("first", story.newest("workers"))
    first_worker = story.agents.workers.first()
    story.agent_starts_role_session(first_worker).expect_allowed(first_worker)
    story.expect_openrig_seat_environment(first_worker, "role:alpha/builder")
    story.expect_role_job_prompt(first_worker, MULTI_POINT_BRIEF, "old task brief", "journal clock-in")
    story.agent_runs_from_openrig_organization_seat(first_worker, "role:alpha/builder", "clock-in").expect_command_passed()

    second_started = story.agent_runs_as_organization_seat(
        domain, "domain:alpha",
        f'organization part {parent} role:alpha/maker "second part" --brief "- the second part is complete"',
    )
    second_started.expect_command_passed()
    second_part = story.newest("tasks")
    story.fixture.workers.__setattr__("second", story.newest("workers"))
    second_worker = story.agents.workers.second()
    story.agent_starts_role_session(second_worker).expect_allowed(second_worker)
    story.expect_openrig_seat_environment(second_worker, "role:alpha/maker")
    story.expect_role_job_prompt(second_worker, "- the second part is complete", "old task brief", "journal clock-in")
    story.agent_runs_from_openrig_organization_seat(second_worker, "role:alpha/maker", "clock-in").expect_command_passed()

    story.agent_proves(first_worker, 1, "the first point is met")
    story.agent_proves(first_worker, 2, "the second point is met")
    story.agent_clocks_out(first_worker, "both points of the first part are met").expect_command_passed()
    story.agent_proves(second_worker, 1, "the second part is complete")
    story.agent_clocks_out(second_worker, "the second part is complete").expect_command_passed()

    refused = story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {first_part} plan",
    )
    refused.expect_command_refused()
    refused.expect_command_text(
        OrganizationNudges.ROLE_WORK_AWAITS_CHECK.create(worker=first_worker.number, task=first_part).rendered(),
    )

    listed = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization parts {parent}",
    )
    listed.expect_command_passed()
    listed.expect_command_text(
        f"task {first_part} started, role:alpha/builder, waits for check from worker {first_worker.number}"
    )
    listed.expect_command_text(
        f"task {second_part} started, role:alpha/maker, waits for check from worker {second_worker.number}"
    )

    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"worker check {first_worker.number} 1",
    ).expect_command_passed()
    still_refused = story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {first_part} plan",
    )
    still_refused.expect_command_refused()
    still_refused.expect_command_text(
        OrganizationNudges.ROLE_WORK_AWAITS_CHECK.create(worker=first_worker.number, task=first_part).rendered(),
    )
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"worker check {first_worker.number} 2",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {first_part} plan",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"worker check {second_worker.number} 1",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {second_part} plan",
    ).expect_command_passed()

    story.organization_seat_goes_idle(domain, "domain:alpha")
    story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"worker merge {first_worker.number}",
    ).expect_command_passed()
    story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"worker merge {second_worker.number}",
    ).expect_command_passed()

    story.expect_task(first_part, state=TaskState.COMPLETED)
    story.expect_task(second_part, state=TaskState.COMPLETED)
    story.expect_task(parent, state=TaskState.COMPLETED)
    story.expect_worker(first_worker, state=WorkerState.MERGED)
    story.expect_worker(second_worker, state=WorkerState.MERGED)
    story.expect_plan(plan, state=PlanState.FINISHED)
    story.expect_stack(domain, LeadingPlan, FollowingPlan, awaiting_state(story))
