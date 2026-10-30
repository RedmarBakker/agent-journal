from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.support.plan_approval import PlanApproval
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, WorkersOptions
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.orchestrator_ready_plan import OrchestratorReadyPlan
from tests.stories.fixtures.main.orchestrator_user_plan import OrchestratorUserPlan


@story(OrchestratorReadyPlan, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
def test_the_orchestrator_approves_no_plan_while_the_user_has_not_allowed_it(story):
    story.agent_runs(story.agents.subject, f"plan approve {story.plans.first}")
    story.expect_command_text("only the user approves")
    story.expect_task(story.tasks.slab, state="open")
    story.expect_stack(story.agents.subject, Orchestrating)


@story(OrchestratorReadyPlan, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.ORCHESTRATOR_APPROVES_PLANS, True)
@setting(WorkersOptions.ORCHESTRATOR_PLAN_APPROVAL, PlanApproval.OWN.value)
def test_an_orchestrator_allowed_its_own_plans_approves_the_plan_it_wrote(story):
    story.agent_runs(story.agents.subject, f"plan approve {story.plans.first}")
    story.expect_command_passed()
    story.expect_plan(story.plans.first, state=PlanState.APPROVED)
    story.expect_task(story.tasks.slab, state="open")
    story.expect_stack(story.agents.subject, Orchestrating)


@story(OrchestratorUserPlan, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.ORCHESTRATOR_APPROVES_PLANS, True)
@setting(WorkersOptions.ORCHESTRATOR_PLAN_APPROVAL, PlanApproval.OWN.value)
def test_an_orchestrator_allowed_its_own_plans_is_refused_the_users_plan_and_may_not_change_the_choice(story):
    story.agent_runs(story.agents.subject, f"plan approve {story.plans.first}")
    story.expect_command_text("only the user approves")
    story.agent_runs(story.agents.subject, f"settings set workers.orchestrator_plan_approval '{PlanApproval.ALL.value}'")
    story.expect_command_text("the user's to set")
    story.expect_task(story.tasks.first, state="open")
    story.expect_task(story.tasks.second, state="open")
    story.expect_stack(story.agents.subject, Orchestrating)


@story(OrchestratorUserPlan, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.ORCHESTRATOR_APPROVES_PLANS, True)
@setting(WorkersOptions.ORCHESTRATOR_PLAN_APPROVAL, PlanApproval.USER_MADE.value)
def test_an_orchestrator_allowed_the_users_plans_approves_the_plan_the_user_made(story):
    story.agent_runs(story.agents.subject, f"plan approve {story.plans.first}")
    story.expect_command_passed()
    story.expect_plan(story.plans.first, state=PlanState.APPROVED)
    story.expect_task(story.tasks.first, state="open")
    story.expect_task(story.tasks.second, state="open")
    story.expect_stack(story.agents.subject, Orchestrating)


@story(OrchestratorReadyPlan, mode=ORCHESTRATOR_MODE, subject=AgentRole.MAIN)
@setting(WorkersOptions.ORCHESTRATOR_APPROVES_PLANS, True)
@setting(WorkersOptions.ORCHESTRATOR_PLAN_APPROVAL, PlanApproval.USER_MADE.value)
def test_an_orchestrator_allowed_the_users_plans_may_not_approve_its_own(story):
    story.agent_runs(story.agents.subject, f"plan approve {story.plans.first}")
    story.expect_command_text("only the user approves")
    story.expect_task(story.tasks.slab, state="open")
    story.expect_stack(story.agents.subject, Orchestrating)
