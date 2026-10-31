from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.feature import Plans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.skills.skills_options import SkillsOptions
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_without_domain_seats import OrganizationPlanWithoutDomainSeats


@story(OrganizationPlanWithoutDomainSeats, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_domain_keeps_its_inbox_handoff_after_a_plans_skill_interrupts_it(story):
    plan, task = story.plans.first, story.tasks.first
    environment = story.openrig_organization_seat_environment("plan")["JOURNAL_ENV"]
    story.user_sets_in_environment(
        SkillsOptions.START_SKILLS, [*SkillsOptions.START_SKILLS.default, "plans"], environment,
    )
    handed = story.agent_runs_from_plan_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    handed.expect_command_passed()
    domain = story.organization_seat_agent("domain:alpha")
    story.expect_openrig_seat_received(
        domain, f"plan-{plan}", "domain:alpha", OrganizationSeatRouting.handoff_prompt,
    )
    started = story.agent_starts_organization_seat(domain, "domain:alpha")
    started.expect_allowed(domain)

    inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")
    inbox.expect_agent_not_told(domain, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                task=task, domain="alpha")

    interrupted = story.agent_reads_in_environment(domain, environment, "source/NOTES.md")
    interrupted.expect_refused(domain, SkillsNudges.SKILL_READ_REQUEST)
    interrupted.expect_agent_told_words(domain, SkillsNudges.SKILL_READ_REQUEST, "the plans skill")
    read = story.agent_reads_a_skill_in_environment(domain, environment, Plans.skill.folder)
    read.expect_allowed(domain)

    inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")
    inbox.expect_agent_not_told(domain, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                task=task, domain="alpha")
    story.expect_stack(domain, LeadingPlan, FollowingPlan)
