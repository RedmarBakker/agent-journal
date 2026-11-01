from journal.engine.states.ended import Ended
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_task_two_parts_clocked_in import OrganizationTaskTwoPartsClockedIn


@story(OrganizationTaskTwoPartsClockedIn, subject=AgentRole.MAIN)
def test_a_domain_checks_clocked_out_split_parts_and_returns_the_parent_after_both_merge(story):
    plan, parent = story.plans.first, story.tasks.first
    first_part, second_part = story.tasks.first_part, story.tasks.second_part
    first_worker, second_worker = story.agents.workers.first(), story.agents.workers.second()
    domain = story.organization_seat_agent("domain:alpha")
    story.organization_seat_goes_idle(domain, "domain:alpha")

    story.agent_proves(second_worker, 1, "the first maker point is met")
    story.agent_proves(second_worker, 2, "the second maker point is met")
    story.agent_clocks_out(second_worker, "both maker points are met").expect_command_passed()
    story.expect_openrig_seat_received(
        domain, story.plan_rig_name(plan), "domain:alpha",
        OrganizationNudges.ROLE_WORK_AWAITS_CHECK.create(worker=second_worker.number, task=second_part).rendered(),
    )
    story.agent_proves(first_worker, 1, "the current task brief is met: the part work is met")
    story.agent_clocks_out(first_worker, "the part work is met").expect_command_passed()
    story.expect_openrig_seat_received(
        domain, story.plan_rig_name(plan), "domain:alpha",
        OrganizationNudges.ROLE_WORK_AWAITS_CHECK.create(worker=first_worker.number, task=first_part).rendered(),
    )

    started = story.agent_starts_organization_seat(domain, "domain:alpha")
    started.expect_agent_told(
        domain, OrganizationNudges.ROLE_WORK_AWAITS_CHECK, worker=first_worker.number, task=first_part,
    )
    started.expect_agent_told(
        domain, OrganizationNudges.ROLE_WORK_AWAITS_CHECK, worker=second_worker.number, task=second_part,
    )
    parts = story.agent_runs_as_organization_seat(domain, "domain:alpha", f"organization parts {parent}")
    parts.expect_command_passed()
    parts.expect_command_text(
        f"task {first_part} started, role:alpha/builder, waits for check from worker {first_worker.number}"
    )
    parts.expect_command_text(
        f"task {second_part} started, role:alpha/maker, waits for check from worker {second_worker.number}"
    )
    stopped = story.agent_stops_organization_seat(domain, "domain:alpha")
    stopped.expect_refused(
        domain, OrganizationNudges.ROLE_WORK_AWAITS_CHECK, worker=first_worker.number, task=first_part,
    )

    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"worker check {first_worker.number} 1",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {first_part} plan",
    ).expect_command_passed()
    next_stop = story.agent_stops_organization_seat(domain, "domain:alpha")
    next_stop.expect_refused(
        domain, OrganizationNudges.ROLE_WORK_AWAITS_CHECK, worker=second_worker.number, task=second_part,
    )
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"worker check {second_worker.number} 1",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"worker check {second_worker.number} 2",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {second_part} plan",
    ).expect_command_passed()

    story.organization_seat_goes_idle(domain, "domain:alpha")
    story.agent_runs_as_organization_seat(
        story.agents.subject, "plan", f"worker merge {first_worker.number}",
    ).expect_command_passed()
    merged = story.agent_runs_as_organization_seat(
        story.agents.subject, "plan", f"worker merge {second_worker.number}",
    )
    merged.expect_command_passed()

    story.expect_task(first_part, state=TaskState.COMPLETED)
    story.expect_task(second_part, state=TaskState.COMPLETED)
    story.expect_task(parent, state=TaskState.COMPLETED)
    story.expect_worker(first_worker, state=WorkerState.MERGED)
    story.expect_worker(second_worker, state=WorkerState.MERGED)
    story.expect_plan(plan, state=PlanState.FINISHED)
    story.expect_openrig_seat_received(
        domain, story.plan_rig_name(plan), "domain:alpha",
        OrganizationNudges.SPLIT_TASK_COMPLETED.create(task=parent).rendered(),
    )
    story.expect_stack(domain, LeadingPlan, Ended)
