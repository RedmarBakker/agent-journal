from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.states.soloing import Soloing
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, SOLO_MODE, WorkersOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.orchestrator_started_plans import OrchestratorStartedPlans
from tests.stories.fixtures.main.three_approved_plans import ThreeApprovedPlans


@story(ThreeApprovedPlans, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_second_plan_the_user_starts_for_a_builder_pauses_the_first_and_the_builder_is_never_asked_about_returning_to_it(story):
    story.agent_runs(story.agents.subject, f"plan start {story.plans.first}")
    story.agent_runs(story.agents.subject, f"task block {story.tasks.first} 'billing comes first'")
    story.user_starts_plan(story.plans.second)
    story.expect_plan(story.plans.first, state=PlanState.PAUSED)
    story.expect_plan(story.plans.second, state=PlanState.STARTED)
    story.expect_plan(story.plans.third, state=PlanState.APPROVED)
    story.expect_task(story.tasks.invoice, state=TaskState.STARTED)
    result = story.agent_writes(story.agents.subject, "invoice.py")
    result.expect_allowed()
    result.expect_agent_not_told(story.agents.subject, PlansNudges.PLAN_RETURN_QUESTION)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan, Working)


@story(OrchestratorStartedPlans, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_an_orchestrator_keeps_every_plan_it_starts_and_a_switch_to_the_builder_keeps_the_one_furthest_along(story):
    story.agent_runs(story.agents.subject, f"plan start {story.plans.third}")
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_plan(story.plans.third, state=PlanState.STARTED)
    story.agent_runs(story.agents.subject, f"task start {story.tasks.invoice}")
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.invoice} --how 'sent'")
    story.user_sets(WorkersOptions.MODE, BUILDER_MODE)
    story.expect_plan(story.plans.first, state=PlanState.PAUSED)
    story.expect_plan(story.plans.second, state=PlanState.STARTED)
    story.expect_plan(story.plans.third, state=PlanState.PAUSED)
    story.expect_stack(story.agents.subject, Ready)


@story(OrchestratorStartedPlans, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_a_switch_to_solo_with_no_plan_further_along_keeps_the_oldest(story):
    story.user_sets(WorkersOptions.MODE, SOLO_MODE)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_plan(story.plans.second, state=PlanState.PAUSED)
    story.expect_plan(story.plans.third, state=PlanState.APPROVED)
    story.expect_stack(story.agents.subject, Soloing)
