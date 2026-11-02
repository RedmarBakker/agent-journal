from journal.engine.states.ended import Ended
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.agent import Agent
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from tests.stories.fixtures.main.organization_plan_handoff_seat import OrganizationPlanHandoffSeat


class PausedOrganizationPlanWithOldAgentRow(OrganizationPlanHandoffSeat):
    """A paused organization plan has an old generic main row beside its prepared Plan agent."""

    parent = OrganizationPlanHandoffSeat

    def steps(self, story) -> None:
        plan = self.plans.first
        story.user_pauses_plan(plan).expect_viewer_passed()
        story.settle()
        environment = story.app.container.get(Environments).existing(f"plan-{plan}")
        plan_row = story.app.container.get(Plans).global_matching(id=plan)[0]
        plan_agent = story.app.container.get(PlanAgents).agent(plan_row)
        ended = Ended()
        with story.app.container.get(Scope).environment(environment.row_id):
            stack = (*plan_agent.stack, {"state": ended.name, "data": ended.serialized()})
            story.app.container.get(Agents).save(plan_agent.with_(state=ended.name, data=ended.serialized(), stack=stack), Actor.system())
        floor = CoordinatingPlans()
        row = Agent(
            environment_id=environment.row_id,
            session="old-plan-agent-session",
            provider=story.provider,
            state=floor.name,
            data=floor.serialized(),
            stack=({"state": floor.name, "data": floor.serialized()},),
            role=AgentRole.MAIN,
        )
        with story.app.container.get(Scope).environment(environment.row_id):
            story.app.container.get(Agents).save(row, Actor.system())
        story.session_environments["old-plan-agent-session"] = environment.name

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.PAUSED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan, Ended)
