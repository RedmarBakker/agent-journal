from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.models.plan_state import PlanState
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_agent_supervisor_gone import PlanAgentSupervisorGone
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION
from journal.supervisor_link import SupervisorLink


def plan_agent() -> StoryAgent:
    return StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)


@story(PlanAgentSupervisorGone, subject=AgentRole.MAIN)
def test_a_started_plan_agent_relaunches_when_the_journal_starts_without_its_supervisor(story):
    plan = story.plans.first
    environment = story.app.container.get(AgentEnvironments).environments.existing(f"plan-{plan}")
    running = set()

    def supervisor_runs(_link: SupervisorLink, environment_id: int) -> bool:
        return environment_id in running

    def launch(_places: AgentEnvironments, launched_environment, _agent, _repositories=()) -> None:
        running.add(launched_environment.row_id)

    story.monkeypatch.setattr(SupervisorLink, "runs", supervisor_runs)
    story.monkeypatch.setattr(AgentEnvironments, "launched", launch)
    story.journal_starts_again()

    result = story.agent_runs(story.agents.subject, f"plan show {plan}")
    result.expect_command_text(f"Plan agent: environment plan-{plan}, running")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_stack(plan_agent(), LeadingPlan, FollowingPlan)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)
