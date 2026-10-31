from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.estimates.estimates_nudges import EstimatesNudges
from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.draft_plan import DraftPlan
from tests.stories.fixtures.main.domain_policy_plan import DomainPolicyPlan
from tests.stories.fixtures.main.enforced_dependency_plan import EnforcedDependencyPlan
from tests.stories.fixtures.main.enforced_draft_plan import EnforcedDraftPlan
from tests.stories.fixtures.main.enforced_draft_without_done import EnforcedDraftWithoutDone


@story(EnforcedDraftPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_enforced_plan_refuses_an_unknown_size_with_a_correction(story):
    story.agent_runs(story.agents.subject, f"plan mode {story.plans.first} organization")
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Delivery' --when 'production accepts the revision'")
    result = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'release' --brief 'the release is deployed' --domain development --phase 1")
    result.expect_command_passed()
    task = story.created_number("task")

    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text(f"task size {task}")
    result.expect_command_text("estimates.size_scale")
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(task, state=TaskState.OPEN, size=None)
    story.expect_stack(story.agents.subject, Ready)


@story(EnforcedDraftPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_enforced_plan_refuses_a_sized_task_without_an_accountable_domain(story):
    story.agent_runs(story.agents.subject, f"plan mode {story.plans.first} organization")
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Delivery' --when 'production accepts the revision'")
    result = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'build' --brief 'the artifact builds' --domain development --size 3 --phase 1")
    result.expect_command_passed()
    first = story.created_number("task")
    result = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'release' --brief 'the release is deployed' --size 3 --phase 1")
    result.expect_command_passed()
    task = story.created_number("task")

    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text(f"plan add {story.plans.first}")
    result.expect_command_text("--domain")
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(first, state=TaskState.OPEN, size=3)
    story.expect_task(task, state=TaskState.OPEN, size=3)
    story.expect_stack(story.agents.subject, Ready)


@story(EnforcedDraftWithoutDone, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_enforced_plan_refuses_a_domain_without_delivery_criteria(story):
    story.agent_runs(story.agents.subject, f"plan mode {story.plans.first} organization")
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Delivery' --when 'production accepts the revision'")
    result = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'release' --brief 'the release is deployed' --domain development --size 3 --phase 1")
    result.expect_command_passed()
    task = story.created_number("task")

    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text("definition of done")
    result.expect_command_text("domain.toml")
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(task, state=TaskState.OPEN, size=3)
    story.expect_stack(story.agents.subject, Ready)


@story(EnforcedDependencyPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_fully_sized_domain_scoped_plan_with_valid_prerequisites_can_be_readied(story):
    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_passed()
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.FORECAST_BASIS, "Not enough history yet")
    story.expect_plan(story.plans.first, state=PlanState.READY)
    story.expect_task(story.tasks.first, state=TaskState.OPEN, size=3)
    story.expect_task(story.tasks.second, state=TaskState.OPEN, size=5)
    story.expect_stack(story.agents.subject, Ready)


@story(DomainPolicyPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_drafted_before_enforcement_is_not_retroactively_trapped(story):
    story.agent_runs(story.agents.subject, f"plan mode {story.plans.first} organization")
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Delivery' --when 'production accepts the revision'")
    story.agent_runs(story.agents.subject, f"plan todos {story.plans.first} 1 {story.tasks.first}")
    story.user_sets(EstimatesOptions.MODE, "enforce")

    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_passed()
    story.expect_plan(story.plans.first, state=PlanState.READY)
    story.expect_task(story.tasks.first, state=TaskState.OPEN, size=None)
    story.expect_stack(story.agents.subject, Ready)


@story(EnforcedDraftPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_solo_plan_cannot_be_readied_when_an_organization_is_configured(story):
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Delivery' --when 'production accepts the revision'")
    story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'release' --brief 'the release is deployed' --size 3 --phase 1")

    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text("organization mode")
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_stack(story.agents.subject, Ready)


@story(EnforcedDependencyPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_plan_show_lists_each_task_size_prerequisite_and_domain(story):
    result = story.agent_runs(story.agents.subject, f"plan show {story.plans.first}")
    result.expect_command_text("size:3")
    result.expect_command_text("after:none")
    result.expect_command_text("domain:development")
    result.expect_command_text(f"after:{story.tasks.first}")
    result.expect_command_text("size:5")
    story.expect_task(story.tasks.second, state=TaskState.OPEN, size=5)
    story.expect_stack(story.agents.subject, Ready)


@story(DraftPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_building_a_plan_asks_for_size_order_mode_domains_priorities_and_review(story):
    result = story.agent_runs(story.agents.subject, "sequence follow")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, "sequence next")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, "sequence follow")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, "sequence next")
    result.expect_command_passed()
    for words in (
        ("estimates.size_scale",),
        ("--after",),
        ("plan mode", "--domain", "Roles"),
        ("--priority",),
        ("journal plan review",),
        ("journal plan ready",),
    ):
        result = story.agent_runs(story.agents.subject, "sequence follow")
        result.expect_command_passed()
        result = story.agent_runs(story.agents.subject, "sequence next")
        result.expect_command_passed()
        for word in words:
            result.expect_command_text(word)
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(EnforcedDraftPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_user_message_about_organization_domains_or_roles_requires_the_organization_skill(story):
    story.agent_reads_a_skill(story.agents.subject, "journal-messages")
    story.agent_reads_a_skill(story.agents.subject, "journal-plans")
    message = story.user_sends_message("Use our organization's Domains and Roles for delivery.")
    story.agent_reads_message(story.agents.subject, message)
    result = story.agent_writes(story.agents.subject, "plan-notes.md")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    result.expect_agent_told_words(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST, "organization-seat-routing")
    story.agent_reads_a_skill(story.agents.subject, OrganizationSeatRouting.skill.folder)
    result = story.agent_writes(story.agents.subject, "plan-notes.md")
    result.expect_allowed()
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_stack(story.agents.subject, Ready)
