from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.support.agent_role import AgentRole
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_domain_role_task import OrganizationDomainRoleTask
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


@story(OrganizationHubPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_seat_hands_a_task_to_its_domain_seat(story):
    task = story.tasks.first
    result = story.agent_runs_from_organization_seat(story.agents.main, "plan", f"organization handoff {task} domain:alpha")
    result.expect_command_passed()
    result.expect_command_text(f"task {task} routed from plan to domain:alpha")
    story.expect_task_tied_to_domain(task, "alpha")
    inbox = story.agent_runs_from_organization_seat(story.agents.main, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {story.plans.first} task {task}: first")
    story.expect_stack(story.agents.main, Ready)


@story(OrganizationDomainRoleTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_domain_handoff_gives_its_role_the_brief_before_the_plan_merges_it(story):
    task = story.tasks.second
    brief = "- task 6 has its current brief"
    old_brief = "- first is done"
    inbox = story.agent_runs_from_organization_seat(story.agents.main, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {story.plans.first} task {task}: task 6 current")
    inbox.expect_command_text(brief)

    result = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    result.expect_command_passed()
    result.expect_command_text(f"task {task} routed from domain:alpha to role:alpha/builder")
    worker_number = story.newest("workers")
    story.fixture.workers.first = worker_number
    worker = story.agents.workers.first()
    story.expect_worker_role_job(worker, task, brief, old_brief)
    story.expect_role_job_prompt(worker, brief, old_brief, f"You are worker {worker}; task {task} is yours", "journal clock-in")
    story.expect_role_guidance_and_skills_omit(worker, "task 6 current", brief, old_brief)

    story.agent_starts_role_session(worker)
    story.expect_openrig_seat_environment(worker, "role:alpha/builder")
    inbox = story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(brief)
    inbox.expect_command_text(f"You are worker {worker}; task {task} is yours")
    clocked_in = story.agent_clocks_in(worker)
    clocked_in.expect_command_text(f"You are worker {worker}; task {task} is yours")
    story.agent_reads(worker).expect_allowed()
    story.agent_proves(worker, 1, f"the current task brief is met: {brief}")
    story.agent_clocks_out(worker, "task 6 is complete")

    refused = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:beta", f"worker check {worker} 1",
    )
    refused.expect_command_refused()
    refused.expect_command_text(f"worker {worker} is not assigned to a Role in domain beta")
    checked = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"worker check {worker} 1",
    )
    checked.expect_command_passed()
    handed_back = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} plan",
    )
    handed_back.expect_command_passed()
    plan_inbox = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "organization inbox")
    plan_inbox.expect_command_passed()
    plan_inbox.expect_command_text(f"worker {worker} holds this task")
    merged = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"worker merge {worker}")
    merged.expect_command_passed()
    merged.expect_command_text(f"task {task} done")

    story.expect_task(story.tasks.first, state=TaskState.COMPLETED)
    story.expect_task(task, state=TaskState.COMPLETED)
    story.expect_worker(worker, state=WorkerState.MERGED)
    story.expect_plan(story.plans.first, state=PlanState.FINISHED)
    story.expect_organization_seat_routing_guidance(f"plan-{story.plans.first}")
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


@story(OrganizationDomainRoleTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_read_only_role_receives_its_inbox_handoff_without_a_worker_job(story):
    task = story.tasks.second
    result = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/scout",
    )
    result.expect_command_passed()
    inbox = story.agent_runs_from_organization_seat(story.agents.main, "role:alpha/scout", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {story.plans.first} task {task}: task 6 current")
    inbox.expect_command_text_without("worker ")
    story.expect_row_count("workers", 0)
    story.expect_task(story.tasks.first, state=TaskState.COMPLETED)
    story.expect_task(task, delegated=False)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


@story(OrganizationHubPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_role_seat_sending_sideways_is_refused_with_its_domain_hub(story):
    task = story.tasks.first
    result = story.agent_runs_from_organization_seat(story.agents.main, "role:alpha/builder", f"organization handoff {task} role:beta/reviewer")
    result.expect_command_refused()
    result.expect_command_text("Send it to your Domain agent, domain:alpha")
    inbox = story.agent_runs_from_organization_seat(story.agents.main, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"no tasks handed to domain:alpha")
    story.expect_stack(story.agents.main, Ready)
