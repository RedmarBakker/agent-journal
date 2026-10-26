from journal.events.agent.agent_event import AgentEvent
from journal.events.agent_listener import AgentListener
from journal.models.plan import Plan
from journal.repositories.agents import Agents
from journal.repositories.plan_reviews import PlanReviews
from journal.repositories.plans import Plans
from journal.support.actor import Actor
from journal.features.workers.support.subagent_entries import SubagentEntries


class CountPlanReviewers(AgentListener[AgentEvent]):
    """A plan in review keeps the count of its reviewers still out: the subagents of the live agents dispatched since its review round opened whose brief names it, so a reviewer coming back changes the plan the viewer shows, and a subagent sent before the round never counts."""

    def __init__(self, plans: Plans, agents: Agents, subagents: SubagentEntries, reviews: PlanReviews) -> None:
        self.plans, self.agents, self.subagents, self.reviews = plans, agents, subagents, reviews

    def handle(self, event: AgentEvent) -> None:
        for plan in self.plans.reviewing():
            output = self.running_reviewers(plan)
            if output != plan.reviewers:
                self.plans.save(plan.reviewers_counted(output, event.time), Actor.system())

    def running_reviewers(self, plan: Plan) -> int:
        rounds = self.reviews.open_review(plan)
        if not rounds:
            return 0
        start = rounds[0].creation_time.timestamp()
        return sum(row.is_running() for agent in self.agents.active_agents() for row in self.subagents.dispatches_mentioning(agent.session, f"plan {plan.id}", start))
