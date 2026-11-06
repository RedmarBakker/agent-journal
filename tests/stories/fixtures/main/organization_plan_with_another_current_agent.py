from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.agent import Agent
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from tests.stories.fixtures.main.idle_organization_plan_seat import IdleOrganizationPlanSeat


class OrganizationPlanWithAnotherCurrentAgent(IdleOrganizationPlanSeat):
    """A Plan seat's row is followed by a newer unrelated agent in the same environment."""

    parent = IdleOrganizationPlanSeat

    def steps(self, story) -> None:
        environment = story.app.container.get(Environments).existing(f"plan-{self.plans.first}")
        floor = CoordinatingPlans()
        story.app.container.get(Agents).save(Agent(
            environment_id=environment.row_id, session="unrelated-seat-session", provider=story.provider,
            state=floor.name, data=floor.serialized(), stack=({"state": floor.name, "data": floor.serialized()},),
            session_started_at=story.app.container.get(TimeSource).moment(),
        ), Actor.system())
        story.observed("a newer unrelated agent is present beside the Plan seat", None, None)
