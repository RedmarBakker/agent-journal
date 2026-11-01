from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_with_dependent_domains import OrganizationPlanWithDependentDomains


@story(OrganizationPlanWithDependentDomains, subject=AgentRole.MAIN)
def test_a_domain_stop_never_requests_a_dependent_task_from_another_domain(story):
    plan, security, engineering = story.plans.first, story.tasks.first, story.tasks.second
    domain = story.organization_seat_agent("domain:alpha")
    started = story.agent_starts_organization_seat(domain, "domain:alpha")
    started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
    unread_stop = story.agent_stops_organization_seat(domain, "domain:alpha")
    unread_stop.expect_refused(domain, OrganizationNudges.UNREAD_HANDOFF)
    unread_stop.expect_agent_not_told(
        domain, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
        task=engineering, domain="beta",
    )
    inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {security}: first")
    story.agent_runs_as_organization_seat(domain, "domain:alpha", "environment overview").expect_command_passed()

    domain_stop = story.agent_stops_organization_seat(domain, "domain:alpha")
    domain_stop.expect_allowed(domain)
    domain_stop.expect_agent_not_told(
        domain, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
        task=engineering, domain="beta",
    )

    story.expect_stack(domain, LeadingPlan, FollowingPlan)
