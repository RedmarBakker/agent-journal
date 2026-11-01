from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.states.working_task import WorkingTask
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_task_part_clocked_in import (
    OrganizationTaskPartClockedIn,
    PART_BRIEF,
)
from tests.stories.fixtures.main.organization_task_split_domain_read import OrganizationTaskSplitDomainRead
from tests.stories.fixtures.main.organization_task_split_plan import OrganizationTaskSplitPlan
from tests.stories.fixtures.main.organization_task_two_parts_clocked_in import OrganizationTaskTwoPartsClockedIn
from tests.stories.fixtures.main.shared_role_queue import awaiting_state


MAKER_BRIEF = "- the maker part is met"


def _domain(story):
    return story.organization_seat_agent("domain:alpha")


def _plan_agent(story):
    return story.agents.main


def _part(story, parent: int, role: str, title: str, brief: str, after: int = 0):
    ordering = f" --after {after}" if after else ""
    domain, role_id = role.split("/", 1) if "/" in role else ("alpha", role)
    return story.agent_runs_as_organization_seat(
        _domain(story), "domain:alpha",
        f'organization part {parent} role:{domain}/{role_id} "{title}" --brief "{brief}"{ordering}',
    )


def _start_worker(story, role: str, brief: str, name: str):
    story.fixture.workers.__setattr__(name, story.newest("workers"))
    worker = getattr(story.agents.workers, name)()
    story.agent_starts_role_session(worker).expect_allowed(worker)
    story.expect_openrig_seat_environment(worker, f"role:alpha/{role}")
    story.expect_role_job_prompt(worker, brief, "old task brief", "journal clock-in")
    story.agent_runs_from_openrig_organization_seat(worker, f"role:alpha/{role}", "clock-in").expect_command_passed()
    return worker


def _return_part_to_plan(story, part: int, worker, role: str, proofs: tuple[str, ...]):
    for number, proof in enumerate(proofs, start=1):
        story.agent_runs_from_openrig_organization_seat(
            worker, f"role:alpha/{role}", f"proof {number} '{proof}'",
        ).expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        worker, f"role:alpha/{role}", "clock-out 'the assigned part is complete'",
    ).expect_command_passed()
    domain = _domain(story)
    for point in range(1, len(proofs) + 1):
        story.agent_runs_as_organization_seat(
            domain, "domain:alpha", f"worker check {worker.number} {point}",
        ).expect_command_passed()
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {part} plan",
    ).expect_command_passed()
    return worker


@story(OrganizationTaskTwoPartsClockedIn, subject=AgentRole.MAIN)
def test_a_domain_splits_a_task_into_two_parts_and_each_role_gets_its_job(story):
    parent = story.tasks.first
    first_part, second_part = story.tasks.first_part, story.tasks.second_part
    builder, maker = story.agents.workers.first(), story.agents.workers.second()
    parts = story.agent_runs_as_organization_seat(_domain(story), "domain:alpha", f"organization parts {parent}")
    parts.expect_command_passed()
    parts.expect_command_text(f"task {first_part}")
    parts.expect_command_text(f"task {second_part}")
    plain_handoff = story.agent_runs_as_organization_seat(
        _domain(story), "domain:alpha", f"organization handoff {parent} role:alpha/builder",
    )
    plain_handoff.expect_command_refused()
    plain_handoff.expect_command_text(OrganizationNudges.SPLIT_HANDOFF_REQUIRED.create(task=parent).rendered())
    story.expect_task(parent, state=TaskState.OPEN)
    story.expect_task(first_part, delegated=True)
    story.expect_task(second_part, delegated=True)
    story.expect_worker(builder, state=WorkerState.READY)
    story.expect_worker(maker, state=WorkerState.READY)
    story.expect_stack(_domain(story), LeadingPlan, FollowingPlan, awaiting_state(story))


@story(OrganizationTaskPartClockedIn, subject=AgentRole.MAIN)
def test_a_part_that_follows_another_waits_and_the_domain_is_told_when_it_is_ready(story):
    parent, first_part = story.tasks.first, story.tasks.first_part
    worker = story.agents.workers.first()
    domain = _domain(story)
    second = _part(story, parent, "maker", "later part", MAKER_BRIEF, first_part)
    second.expect_command_passed()
    second_part = story.newest("tasks")
    story.expect_task(second_part, state=TaskState.BLOCKED, delegated=False, waits=[f"tasks:{first_part}"])

    story.agent_runs_from_openrig_organization_seat(
        worker, "role:alpha/builder", "proof 1 'the assigned part is complete'",
    ).expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        worker, "role:alpha/builder", "clock-out 'the assigned part is complete'",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat(domain, "domain:alpha", f"worker check {worker.number} 1").expect_command_passed()
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {first_part} plan",
    ).expect_command_passed()
    story.organization_seat_goes_idle(domain, "domain:alpha")
    ready = story.agent_runs_as_organization_seat(
        story.agents.subject, "plan", f"worker merge {worker.number}",
    )
    ready.expect_command_passed()
    story.expect_task(first_part, state=TaskState.COMPLETED)
    story.expect_task(second_part, state=TaskState.OPEN, delegated=False)
    story.expect_openrig_seat_received(
        domain, story.plan_rig_name(story.plans.first), "domain:alpha",
        OrganizationNudges.SPLIT_PART_READY.create(
            task=second_part, role="role:alpha/maker",
        ).rendered(),
    )
    routed = story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {second_part} role:alpha/maker",
    )
    routed.expect_command_passed()
    story.expect_task(second_part, delegated=True)
    story.expect_stack(_domain(story), LeadingPlan, FollowingPlan, awaiting_state(story))


@story(OrganizationTaskPartClockedIn, subject=AgentRole.MAIN)
def test_a_role_cannot_split_and_is_told_to_clock_out(story):
    worker = story.agents.workers.first()
    result = story.agent_runs_from_openrig_organization_seat(
        worker, "role:alpha/builder",
        f'organization part {story.tasks.first_part} role:alpha/maker "nested" --brief "- nested work"',
    )
    result.expect_command_refused()
    result.expect_command_text(OrganizationNudges.ROLE_TASK_RETURN.rendered())
    story.expect_stack(worker, Void, WorkingTask)


@story(OrganizationTaskSplitDomainRead, subject=AgentRole.MAIN)
def test_a_domain_cannot_hand_a_part_to_another_domains_role_and_is_pointed_to_other(story):
    parts = story.agent_runs_as_organization_seat(
        _domain(story), "domain:alpha", f"organization parts {story.tasks.first}",
    )
    parts.expect_command_passed()
    parts.expect_command_text("has no parts")
    result = _part(story, story.tasks.first, "beta/reviewer", "beta part", "- review beta work")
    result.expect_command_refused()
    result.expect_command_text("journal organization other")
    story.expect_task_count(1)
    story.expect_stack(_domain(story), LeadingPlan, FollowingPlan)


@story(OrganizationTaskSplitDomainRead, subject=AgentRole.MAIN)
def test_a_part_for_another_domain_goes_to_the_plan_which_hands_it_on(story):
    result = story.agent_runs_as_organization_seat(
        _domain(story), "domain:alpha",
        f'organization other {story.tasks.first} domain:beta "beta task" --brief "- beta work"',
    )
    result.expect_command_passed()
    task = story.newest("tasks")
    plan = _plan_agent(story)
    story.expect_openrig_seat_received(
        plan, story.plan_rig_name(story.plans.first), "plan", OrganizationSeatRouting.handoff_prompt,
    )
    plan_prompt = story.agent_resumes_the_session(plan)
    plan_prompt.expect_agent_told(plan, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                  task=task, domain="beta")
    handoff = story.agent_runs_as_organization_seat(plan, "plan", f"organization handoff {task} domain:beta")
    handoff.expect_command_passed()
    beta = story.organization_seat_agent("domain:beta")
    story.agent_starts_organization_seat(beta, "domain:beta").expect_allowed(beta)
    inbox = story.agent_runs_as_organization_seat(beta, "domain:beta", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"task {task}: beta task")
    story.expect_task_tied_to_domain(task, "beta")
    story.expect_stack(beta, LeadingPlan, FollowingPlan)


@story(OrganizationTaskPartClockedIn, subject=AgentRole.MAIN)
def test_a_part_cannot_have_parts_and_an_after_cycle_is_refused(story):
    nested = _part(story, story.tasks.first_part, "maker", "nested part", "- nested work")
    nested.expect_command_refused()
    cycle = _part(story, story.tasks.first, "maker", "cycle", "- cycle work", story.tasks.first)
    cycle.expect_command_refused()
    held_parent = story.user_adds_plan_task(story.plans.first, "held parent", "alpha")
    story.agent_runs_from_plan_organization_seat(
        story.agents.subject, "plan", f"organization handoff {held_parent} domain:alpha",
    ).expect_command_passed()
    domain = _domain(story)
    story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox").expect_command_passed()
    story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {held_parent} role:alpha/builder",
    ).expect_command_passed()
    held = _part(story, held_parent, "maker", "held part", "- held work")
    held.expect_command_refused()
    held.expect_command_text("queued for worker")
    story.expect_task_count(3)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_stack(domain, LeadingPlan, FollowingPlan, awaiting_state(story))


@story(OrganizationTaskTwoPartsClockedIn, subject=AgentRole.MAIN)
def test_the_plan_task_is_completed_when_the_last_part_is_checked_and_merged(story):
    parent, first_part, second_part = story.tasks.first, story.tasks.first_part, story.tasks.second_part
    builder, maker = story.agents.workers.first(), story.agents.workers.second()
    _return_part_to_plan(story, first_part, builder, "builder", ("the part work is met",))
    _return_part_to_plan(
        story, second_part, maker, "maker",
        ("the first maker point is met", "the second maker point is met"),
    )

    plan = _plan_agent(story)
    resumed = story.organization_seat_hook(
        plan, "plan", "SessionStart", "Plan seat receives checked parts", source="resume",
    )
    resumed.expect_agent_told(
        plan, OrganizationNudges.SPLIT_PART_WAITING_FOR_MERGE,
        worker=builder.number, task=first_part,
    )
    resumed.expect_agent_told(
        plan, OrganizationNudges.SPLIT_PART_WAITING_FOR_MERGE,
        worker=maker.number, task=second_part,
    )
    inbox = story.agent_runs_as_organization_seat(plan, "plan", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {story.plans.first} task {first_part}: first part")
    inbox.expect_command_text(f"worker {builder.number} holds this task")
    inbox.expect_command_text(f"journal worker merge {builder.number}")
    inbox.expect_command_text(f"plan {story.plans.first} task {second_part}: second part")
    inbox.expect_command_text(f"worker {maker.number} holds this task")
    inbox.expect_command_text(f"journal worker merge {maker.number}")
    parts = story.agent_runs_as_organization_seat(plan, "plan", f"organization parts {parent}")
    parts.expect_command_passed()
    parts.expect_command_text(f"task {first_part} started, plan, checked and waiting for merge from worker {builder.number}")
    parts.expect_command_text(f"task {second_part} started, plan, checked and waiting for merge from worker {maker.number}")

    story.agent_runs_as_organization_seat(plan, "plan", f"worker merge {builder.number}").expect_command_passed()
    story.expect_task(parent, state=TaskState.OPEN)
    story.agent_runs_as_organization_seat(plan, "plan", f"worker merge {maker.number}").expect_command_passed()
    story.expect_task(second_part, state=TaskState.COMPLETED)
    story.expect_task(parent, state=TaskState.COMPLETED)
    story.expect_plan(story.plans.first, state=PlanState.FINISHED)
    story.expect_openrig_seat_received(
        _domain(story), story.plan_rig_name(story.plans.first), "domain:alpha",
        OrganizationNudges.SPLIT_TASK_COMPLETED.create(task=parent).rendered(),
    )
    story.expect_stack(_domain(story))


@story(OrganizationTaskPartClockedIn, subject=AgentRole.MAIN)
def test_the_plan_seat_sees_split_progress_and_is_not_nudged_again(story):
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_task(story.tasks.first_part, delegated=True)
    resumed = story.organization_seat_hook(
        story.agents.subject, "plan", "SessionStart", "Plan seat resumes its session", source="resume",
    )
    resumed.expect_agent_not_told(
        story.agents.subject, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
        task=story.tasks.first, domain="alpha",
    )
    plans = story.agent_runs_as_organization_seat(story.agents.subject, "plan", "organization plans")
    plans.expect_command_passed()
    plans.expect_command_text("split into 1 part")
    plans.expect_command_text("with its Domain")
    story.expect_stack(_plan_agent(story), LeadingPlan, FollowingPlan, awaiting_state(story))


@story(OrganizationTaskPartClockedIn, subject=AgentRole.MAIN)
def test_a_restarted_plan_reopens_the_domain_inbox_for_unfinished_parts(story):
    plan, part = story.plans.first, story.tasks.first_part
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.user_pauses_plan(plan).expect_viewer_passed()
    story.user_starts_plan(plan).expect_viewer_passed()
    domain = _domain(story)
    started = story.agent_starts_organization_seat(domain, "domain:alpha")
    started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
    inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"task {part}: first part")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(part, delegated=True)
    story.expect_stack(domain, LeadingPlan, FollowingPlan, awaiting_state(story))


@story(OrganizationTaskPartClockedIn, subject=AgentRole.MAIN)
def test_an_ended_role_on_a_part_is_sent_the_part_again(story):
    worker = story.agents.workers.first()
    story.worker_run_ends_without_clocking_out(worker)
    resent = story.agent_runs_as_organization_seat(
        _domain(story), "domain:alpha", f"organization handoff {story.tasks.first_part} role:alpha/builder",
    )
    resent.expect_command_passed()
    story.expect_worker(worker, state=WorkerState.DISPATCHED)
    story.expect_worker_role_job(worker, story.tasks.first_part, PART_BRIEF, "old task brief")
    story.agent_starts_role_session(worker).expect_allowed(worker)
    story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in").expect_command_passed()
    story.expect_stack(worker, Void, WorkingTask)


@story(OrganizationTaskPartClockedIn, subject=AgentRole.MAIN)
def test_a_part_the_domain_refuses_goes_back_to_the_same_role(story):
    worker = story.agents.workers.first()
    story.agent_proves(worker, 1, "the part work is met")
    story.agent_clocks_out(worker, "the part work is met").expect_command_passed()
    story.role_seat_starts_a_new_session(worker, "role:alpha/builder").expect_allowed(worker)
    story.agent_has_written(worker, "the prior Role session ended after reporting its work")
    refused = story.agent_runs_as_organization_seat(
        _domain(story), "domain:alpha", f"worker check {worker.number} 1 --short 'add one missing detail'",
    )
    refused.expect_command_passed()
    story.expect_worker(worker, state=WorkerState.DISPATCHED)
    story.expect_worker(worker.number, brief="Point 1 of task 2 came back short: add one missing detail. Prove it again, then clock out.")
    story.expect_task(story.tasks.first_part, state=TaskState.STARTED, delegated=True)
    story.agent_starts_role_session(worker).expect_allowed(worker)
    story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in").expect_command_passed()
    story.expect_stack(worker, Void, WorkingTask)


@story(OrganizationTaskPartClockedIn, subject=AgentRole.MAIN)
def test_a_cancelled_part_does_not_stop_the_task_but_all_cancelled_parts_are_handed_back(story):
    parent, first_part = story.tasks.first, story.tasks.first_part
    second = _part(story, parent, "maker", "waiting part", MAKER_BRIEF, first_part)
    second.expect_command_passed()
    second_part = story.newest("tasks")
    worker = story.agents.workers.first()
    domain = _domain(story)
    story.worker_run_ends_without_clocking_out(worker)
    story.organization_seat_goes_idle(domain, "domain:alpha")
    story.user_cancels_task(second_part, "the part is no longer needed").expect_viewer_passed()
    story.agent_runs(story.agents.subject, f"worker release {worker.number}").expect_command_passed()
    story.user_cancels_task(first_part, "the part is no longer needed").expect_viewer_passed()
    story.expect_task(parent, state=TaskState.OPEN)
    story.expect_openrig_seat_received(
        domain, story.plan_rig_name(story.plans.first), "domain:alpha",
        OrganizationNudges.SPLIT_ALL_PARTS_CANCELLED.create(task=parent).rendered(),
    )
    story.expect_stack(domain, LeadingPlan, FollowingPlan)


@story(OrganizationTaskSplitPlan, subject=AgentRole.MAIN)
def test_a_shared_role_takes_parts_of_two_plans_in_turn(story):
    first_plan, first_parent = story.plans.first, story.tasks.first
    first_handoff = story.agent_runs_from_plan_organization_seat(
        story.agents.subject, "plan", f"organization handoff {first_parent} domain:alpha",
    )
    first_handoff.expect_command_passed()
    first_domain = story.organization_seat_agent("domain:alpha")
    story.agent_starts_organization_seat(first_domain, "domain:alpha").expect_allowed(first_domain)
    story.agent_runs_as_organization_seat(first_domain, "domain:alpha", "organization inbox").expect_command_passed()
    first_part_result = story.agent_runs_as_organization_seat(
        first_domain, "domain:alpha",
        f'organization part {first_parent} role:alpha/shared "first plan part" --brief "{PART_BRIEF}"',
    )
    first_part_result.expect_command_passed()
    first_part = story.newest("tasks")
    first_worker = story.newest("workers")
    first_role_worker = story.agents.workers.get(first_worker)
    story.agent_starts_role_session(first_role_worker).expect_allowed(first_role_worker)
    story.expect_worker_role_job(first_role_worker, first_part, PART_BRIEF, "old task brief")
    story.agent_runs_from_openrig_organization_seat(first_role_worker, "role:alpha/shared", "clock-in").expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        first_role_worker, "role:alpha/shared", "proof 1 'the first plan part is complete'",
    ).expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        first_role_worker, "role:alpha/shared", "clock-out 'the first plan part is complete'",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat(
        first_domain, "domain:alpha", f"worker check {first_worker} 1",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat(
        first_domain, "domain:alpha", f"organization handoff {first_part} plan",
    ).expect_command_passed()
    story.organization_seat_goes_idle(first_domain, "domain:alpha")
    first_merged = story.agent_runs_as_organization_seat_without_settling(
        story.agents.subject, "plan", f"worker merge {first_worker}",
    )
    first_merged.expect_command_passed()
    story.expect_stack(first_domain, LeadingPlan, Ended)
    story.expect_task(first_part, state=TaskState.COMPLETED)
    story.expect_task(first_parent, state=TaskState.COMPLETED)
    story.expect_worker(first_role_worker, state=WorkerState.MERGED)
    story.expect_plan(first_plan, state=PlanState.FINISHED)

    second_plan = story.user_creates_plan("Second plan", "Finish the second organization plan")
    second_parent = story.user_adds_plan_task(second_plan, "second parent", "alpha")
    story.agent_runs(story.agents.subject, f"plan mode {second_plan} organization").expect_command_passed()
    story.user_approves_plan(second_plan).expect_viewer_passed()
    story.user_starts_plan(second_plan).expect_viewer_passed()
    second_plan_seat = story.organization_seat_agent_in_plan("plan", second_plan)
    story.agent_starts_organization_seat_in_plan(second_plan_seat, "plan", second_plan).expect_allowed(second_plan_seat)
    second_handoff = story.agent_runs_as_organization_seat_in_plan(
        second_plan_seat, "plan", second_plan, f"organization handoff {second_parent} domain:alpha",
    )
    second_handoff.expect_command_passed()
    second_domain = story.organization_seat_agent_in_plan("domain:alpha", second_plan)
    story.agent_starts_organization_seat_in_plan(second_domain, "domain:alpha", second_plan).expect_allowed(second_domain)
    story.agent_runs_as_organization_seat_in_plan(second_domain, "domain:alpha", second_plan, "organization inbox").expect_command_passed()
    second_part_result = story.agent_runs_as_organization_seat_in_plan(
        second_domain, "domain:alpha", second_plan,
        f'organization part {second_parent} role:alpha/shared "second plan part" --brief "{MAKER_BRIEF}"',
    )
    second_part_result.expect_command_passed()
    second_part = story.newest("tasks")
    second_worker = story.newest("workers")
    second_role_worker = story.agents.workers.get(second_worker)
    story.expect_row_count("workers", 2)
    story.expect_task(second_part, delegated=True)
    story.agent_starts_role_session(second_role_worker).expect_allowed(second_role_worker)
    story.expect_worker_role_job(second_role_worker, second_part, MAKER_BRIEF, "old task brief")
    story.agent_runs_from_openrig_organization_seat(
        second_role_worker, "role:alpha/shared", "clock-in",
    ).expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        second_role_worker, "role:alpha/shared", "proof 1 'the second plan part is complete'",
    ).expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        second_role_worker, "role:alpha/shared", "clock-out 'the second plan part is complete'",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat_in_plan(
        second_domain, "domain:alpha", second_plan, f"worker check {second_worker} 1",
    ).expect_command_passed()
    story.agent_runs_as_organization_seat_in_plan(
        second_domain, "domain:alpha", second_plan, f"organization handoff {second_part} plan",
    ).expect_command_passed()
    story.organization_seat_goes_idle(second_domain, "domain:alpha")
    second_merged = story.agent_runs_as_organization_seat_in_plan_without_settling(
        second_plan_seat, "plan", second_plan, f"worker merge {second_worker}",
    )
    second_merged.expect_command_passed()
    story.expect_stack(second_domain, LeadingPlan, Ended)
    story.expect_task(second_part, state=TaskState.COMPLETED)
    story.expect_task(second_parent, state=TaskState.COMPLETED)
    story.expect_worker(second_role_worker, state=WorkerState.MERGED)
    story.expect_plan(second_plan, state=PlanState.FINISHED)
    story.expect_stack(second_domain, LeadingPlan, Ended)
