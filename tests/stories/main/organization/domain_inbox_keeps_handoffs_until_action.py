from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_domain_seat_started import OrganizationDomainSeatStarted
from tests.stories.fixtures.main.shared_role_queue import awaiting_state


@story(OrganizationDomainSeatStarted, subject=AgentRole.MAIN)
def test_a_domain_keeps_its_inbox_handoff_until_it_hands_the_task_to_a_role(story):
    plan, task = story.plans.first, story.tasks.first
    domain = story.organization_seat_agent("domain:alpha")

    inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")
    inbox.expect_agent_not_told(domain, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                task=task, domain="alpha")

    inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")
    inbox.expect_agent_not_told(domain, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                task=task, domain="alpha")

    handed = story.agent_runs_from_openrig_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    handed.expect_command_passed()
    handed.expect_command_text(f"task {task} routed from domain:alpha to role:alpha/builder")
    inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text("no tasks handed to domain:alpha")
    inbox.expect_command_text_without(f"plan {plan} task {task}: first")
    inbox.expect_agent_not_told(domain, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                task=task, domain="alpha")
    story.expect_stack(domain, LeadingPlan, FollowingPlan, awaiting_state(story))
