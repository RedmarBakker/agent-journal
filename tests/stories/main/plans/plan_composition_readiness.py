from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.estimates.estimates_nudges import EstimatesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.domain_policy_plan import DomainPolicyPlan
from tests.stories.fixtures.main.enforced_dependency_plan import EnforcedDependencyPlan
from tests.stories.fixtures.main.enforced_draft_plan import EnforcedDraftPlan
from tests.stories.fixtures.main.enforced_draft_without_done import EnforcedDraftWithoutDone


@story(EnforcedDraftPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_enforced_plan_refuses_an_unknown_size_with_a_correction(story):
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
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Delivery' --when 'production accepts the revision'")
    result = story.agent_runs(story.agents.subject, f"plan add {story.plans.first} 'release' --brief 'the release is deployed' --size 3 --phase 1")
    result.expect_command_passed()
    task = story.created_number("task")

    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text(f"plan add {story.plans.first}")
    result.expect_command_text("--domain")
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_task(task, state=TaskState.OPEN, size=3)
    story.expect_stack(story.agents.subject, Ready)


@story(EnforcedDraftWithoutDone, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_enforced_plan_refuses_a_domain_without_delivery_criteria(story):
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
    result.expect_agent_told_words(story.agents.subject, EstimatesNudges.FORECAST_BASIS, "not enough history")
    story.expect_plan(story.plans.first, state=PlanState.READY)
    story.expect_task(story.tasks.first, state=TaskState.OPEN, size=3)
    story.expect_task(story.tasks.second, state=TaskState.OPEN, size=5)
    story.expect_stack(story.agents.subject, Ready)


@story(DomainPolicyPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_drafted_before_enforcement_is_not_retroactively_trapped(story):
    story.agent_runs(story.agents.subject, f"plan phase {story.plans.first} 'Delivery' --when 'production accepts the revision'")
    story.agent_runs(story.agents.subject, f"plan todos {story.plans.first} 1 {story.tasks.first}")
    story.user_sets(EstimatesOptions.MODE, "enforce")

    result = story.agent_runs(story.agents.subject, f"plan ready {story.plans.first}")
    result.expect_command_passed()
    story.expect_plan(story.plans.first, state=PlanState.READY)
    story.expect_task(story.tasks.first, state=TaskState.OPEN, size=None)
    story.expect_stack(story.agents.subject, Ready)
