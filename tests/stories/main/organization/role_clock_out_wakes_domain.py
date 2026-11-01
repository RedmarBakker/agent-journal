from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_without_domain_seats import TASK_BRIEF
from tests.stories.fixtures.main.organization_role_worker_clocked_in import OrganizationRoleWorkerClockedIn
from tests.stories.fixtures.main.shared_role_queue import awaiting_state


@story(OrganizationRoleWorkerClockedIn, subject=AgentRole.MAIN)
def test_a_role_clock_out_wakes_its_domain_seat_to_check_and_return_the_task(story):
    plan, task = story.plans.first, story.tasks.first
    domain = story.organization_seat_agent("domain:alpha")
    worker = story.agents.workers.first()
    story.agent_proves(worker, 1, f"the current task brief is met: {TASK_BRIEF.removeprefix('- ')}")
    story.organization_seat_goes_idle(domain, "domain:alpha")

    clocked_out = story.agent_clocks_out(worker, "the task brief is met")
    clocked_out.expect_command_passed()
    story.expect_openrig_seat_received(
        domain, story.plan_rig_name(plan), "domain:alpha",
        f"task {task} from worker {worker.number} waits for your check. `journal worker check {worker.number} <point>`; "
        f"then `journal organization handoff {task} plan`",
    )
    started = story.agent_starts_organization_seat(domain, "domain:alpha")
    started.expect_agent_told(domain, OrganizationNudges.ROLE_WORK_AWAITS_CHECK, worker=worker.number, task=task)

    checked = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", f"worker check {worker} 1")
    checked.expect_command_passed()
    returned = story.agent_runs_from_openrig_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} plan",
    )
    returned.expect_command_passed()
    returned.expect_command_text(f"task {task} routed from domain:alpha to plan")

    story.expect_task(task, state=TaskState.STARTED, delegated=True)
    story.expect_worker(worker, state=WorkerState.DELIVERED)
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_stack(domain, LeadingPlan, FollowingPlan, awaiting_state(story))
