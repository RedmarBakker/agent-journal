from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.feature import Plans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_domain_seat_started import OrganizationDomainSeatStarted


@story(OrganizationDomainSeatStarted, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_domain_keeps_its_inbox_handoff_after_a_plans_skill_interrupts_it(story):
    plan, task = story.plans.first, story.tasks.first
    domain = story.organization_seat_agent("domain:alpha")

    inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")
    inbox.expect_agent_not_told(domain, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                task=task, domain="alpha")

    interrupted = story.agent_reads(domain, "source/NOTES.md")
    interrupted.expect_refused(domain, SkillsNudges.SKILL_READ_REQUEST)
    interrupted.expect_agent_told_words(domain, SkillsNudges.SKILL_READ_REQUEST, "the plans skill")
    read = story.agent_reads_a_skill(domain, Plans.skill.folder)
    read.expect_allowed(domain)

    inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(f"plan {plan} task {task}: first")
    inbox.expect_agent_not_told(domain, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                task=task, domain="alpha")
    story.expect_stack(domain, LeadingPlan, FollowingPlan)
