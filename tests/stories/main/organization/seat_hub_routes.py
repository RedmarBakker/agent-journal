from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_domain_task import OrganizationDomainTask
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


@story(OrganizationDomainTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_domain_seat_hands_its_task_to_a_role_seat(story):
    task = story.tasks.first
    inbox = story.agent_runs_from_organization_seat(story.agents.main, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {story.plans.first} task {task}: first")
    result = story.agent_runs_from_organization_seat(story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder")
    result.expect_command_passed()
    result.expect_command_text(f"task {task} routed from domain:alpha to role:alpha/builder")
    story.expect_task_tied_to_domain(task, "alpha")
    inbox = story.agent_runs_from_organization_seat(story.agents.main, "role:alpha/builder", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {story.plans.first} task {task}: first")
    story.expect_organization_seat_routing_guidance(f"plan-{story.plans.first}")
    story.expect_stack(story.agents.main, Ready)


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
