from journal.engine.states.ended import Ended
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
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
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats


BLOCK_REASON = "the Plan agent session ended"
NEW_PLAN_SESSION = "unblocked-plan-agent-session"


class BlockedOrganizationPlanWithOldAgentRow(OrganizationPlanWithDomainSeats):
    """A blocked organization plan has an ended Plan agent and an older coordinator row."""

    parent = OrganizationPlanWithDomainSeats

    def steps(self, story) -> None:
        plan = self.plans.first
        environment = story.app.container.get(Environments).existing(f"plan-{plan}")
        coordinator = CoordinatingPlans()
        leftover = story.app.container.get(Agents).save(Agent(
            environment_id=environment.row_id,
            session=NEW_PLAN_SESSION,
            provider=story.provider,
            state=coordinator.name,
            data=coordinator.serialized(),
            stack=({"state": coordinator.name, "data": coordinator.serialized()},),
            role=AgentRole.MAIN,
        ), Actor.system())

        story.agent_runs(story.agents.main, f"plan block {plan} '{BLOCK_REASON}'").expect_command_passed()

        plan_row = story.app.container.get(Plans).global_matching(id=plan)[0]
        plan_agent = story.app.container.get(PlanAgents).agent(plan_row)
        ended = Ended()
        stack = (*plan_agent.stack, {"state": ended.name, "data": ended.serialized()})
        coordinator_row = leftover.with_(state=coordinator.name, data=coordinator.serialized(),
                                         stack=({"state": coordinator.name, "data": coordinator.serialized()},))
        with story.app.container.get(Scope).environment(environment.row_id):
            story.app.container.get(Agents).save(plan_agent.with_(state=ended.name, data=ended.serialized(), stack=stack), Actor.system())
            story.app.container.get(Agents).save(coordinator_row, Actor.system())
        story.session_environments[NEW_PLAN_SESSION] = environment.name

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.BLOCKED, block_reason=BLOCK_REASON)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)
        story.expect_stack(StoryAgent(AgentRole.MAIN, session=NEW_PLAN_SESSION), CoordinatingPlans)
