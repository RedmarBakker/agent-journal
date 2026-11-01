from journal.engine.states.void import Void
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, WorkersOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.organization_role_part_clocked_out import OrganizationRolePartClockedOut
from tests.stories.fixtures.main.shared_role_queue import awaiting_state


PART_BRIEF = "- the part work is met"


def _start_second_plan(story):
    plan = story.user_creates_plan("Second plan", "Finish the second organization plan")
    task = story.user_adds_plan_task(plan, "second parent", "alpha")
    story.agent_runs(story.agents.subject, f"plan mode {plan} organization").expect_command_passed()
    story.user_approves_plan(plan).expect_viewer_passed()
    story.user_starts_plan(plan).expect_viewer_passed()
    plan_seat = story.organization_seat_agent_in_plan("plan", plan)
    story.agent_starts_organization_seat_in_plan(plan_seat, "plan", plan).expect_allowed(plan_seat)
    story.agent_runs_as_organization_seat_in_plan(
        plan_seat, "plan", plan, f"organization handoff {task} domain:alpha",
    ).expect_command_passed()
    domain = story.organization_seat_agent_in_plan("domain:alpha", plan)
    story.agent_starts_organization_seat_in_plan(domain, "domain:alpha", plan).expect_allowed(domain)
    story.agent_runs_as_organization_seat_in_plan(domain, "domain:alpha", plan, "organization inbox").expect_command_passed()
    return plan, task, domain


def _make_part(story, domain, plan, parent, role):
    return story.agent_runs_as_organization_seat_in_plan(
        domain, "domain:alpha", plan,
        f'organization part {parent} role:alpha/{role} "second part" --brief "{PART_BRIEF}"',
    )


def _stop_plan_rig(story, plan):
    rig = story.plan_rig_name(plan)
    story.openrig.run("down", rig, "--yes", "--json")
    story.observed(f"OpenRig stops {rig}", None, None)


@story(OrganizationRolePartClockedOut, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.WORKER_LIMIT, 1)
def test_a_clocked_out_role_worker_of_a_paused_plan_does_not_hold_a_place_for_another_plan(story):
    paused_plan = story.plans.first
    old_worker = story.agents.workers.first()
    story.user_pauses_plan(paused_plan).expect_viewer_passed()
    story.expect_plan(paused_plan, state=PlanState.PAUSED)
    _stop_plan_rig(story, paused_plan)

    plan, parent, domain = _start_second_plan(story)
    dispatched = _make_part(story, domain, plan, parent, "maker")
    dispatched.expect_command_passed()
    new_part = story.newest("tasks")
    new_worker = story.newest("workers")
    story.expect_task(new_part, delegated=True)
    story.expect_worker(old_worker, state=WorkerState.DELIVERED)
    story.expect_worker(new_worker, state=WorkerState.DISPATCHED)
    story.expect_stack(domain, LeadingPlan, FollowingPlan, awaiting_state(story))


@story(OrganizationRolePartClockedOut, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.WORKER_LIMIT, 1)
def test_a_role_worker_on_a_plan_whose_rig_is_gone_does_not_hold_a_place(story):
    lost_rig_plan = story.plans.first
    _stop_plan_rig(story, lost_rig_plan)
    story.expect_plan(lost_rig_plan, state=PlanState.STARTED)

    plan, parent, domain = _start_second_plan(story)
    dispatched = _make_part(story, domain, plan, parent, "maker")
    dispatched.expect_command_passed()
    new_part = story.newest("tasks")
    story.expect_task(new_part, delegated=True)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)
    story.expect_worker(story.agents.workers.second(), state=WorkerState.DISPATCHED)
    story.expect_stack(domain, LeadingPlan, FollowingPlan, awaiting_state(story))


@story(OrganizationRolePartClockedOut, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.WORKER_LIMIT, 1)
def test_a_full_place_refusal_routes_another_plans_clocked_out_work_to_its_plan_seat(story):
    old_worker = story.agents.workers.first()
    story.user_sets(WorkersOptions.MODE, ORCHESTRATOR_MODE).expect_viewer_passed()
    plan, parent, domain = _start_second_plan(story)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    refused = _make_part(story, domain, plan, parent, "maker")
    refused.expect_refused_by_anything()
    refused.expect_refusal_text(f"plan {story.plans.first}'s Plan seat must free a place")
    refused.expect_refusal_without(f"worker {old_worker.number}")
    story.expect_row_count("workers", 1)
    story.expect_task(story.tasks.first_part, state=TaskState.STARTED, delegated=True)
    story.expect_stack(domain, LeadingPlan, FollowingPlan, awaiting_state(story))


@story(OrganizationRolePartClockedOut, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.WORKER_LIMIT, 1)
def test_cancelling_a_plan_releases_its_clocked_out_role_worker(story):
    plan, part, worker = story.plans.first, story.tasks.first_part, story.agents.workers.first()
    story.user_cancels_plan(plan).expect_viewer_passed()
    story.expect_plan(plan, state=PlanState.CANCELLED)
    story.expect_task(story.tasks.first, state=TaskState.CANCELLED)
    story.expect_task(part, state=TaskState.CANCELLED)
    story.expect_worker(worker, state=WorkerState.RELEASED)
    story.expect_stack(worker, Void)
