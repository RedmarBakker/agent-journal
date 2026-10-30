import json

from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.plans.support.plan_agents import PlanAgents
from journal.repositories.plans import Plans
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import BUILDER_MODE, setting, story
from tests.stories.fixtures.main.plan_approved import PlanApproved


def recorded_cost(story, session: str, amount: float) -> None:
    path = story.app.config.status_home / f"{session}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"session_id": session, "cost": {"total_cost_usd": amount}}))


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_a_solo_plan_records_its_plan_agent_session_cost(story):
    story.monkeypatch.setattr(AgentEnvironments, "launched", lambda places, environment, agent, repositories=(): None)
    plan = story.plans.first
    story.agent_runs(story.agents.main, f"plan start {plan}")
    plans, agents = story.app.container.get(Plans), story.app.container.get(PlanAgents)
    environment = agents.environment(plans.find(plan))
    session = "plan-agent-cost-session"
    story.session_starts_in(environment.name, session)
    recorded_cost(story, session, 0.12)
    story.user_pauses_plan(plan)
    story.user_starts_plan(plan)
    recorded_cost(story, session, 0.37)
    story.agent_in_runs(story.agents.main, environment.name, session, f"task complete {story.tasks.first} --how done")
    story.agent_in_runs(story.agents.main, environment.name, session, f"task complete {story.tasks.second} --how done")
    story.user_opens(f"/journal/plans/{plan}/team")
    story.expect_viewer_passed()
    story.expect_viewer_shows("estimated_api_cost_usd", 0.37)
    story.expect_stack(story.agents.main, CoordinatingPlans)
