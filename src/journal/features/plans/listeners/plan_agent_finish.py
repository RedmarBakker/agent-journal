from journal.events.listener import Listener
from journal.events.rows.plan_finished import PlanFinished
from journal.features.plans.support.plan_agents import PlanAgents
from journal.features.plans.support.plan_branch_merge import PlanBranchMerge
from journal.models.plan_mode import PlanMode
from journal.repositories.plans import Plans


class PlanAgentFinish(Listener[PlanFinished]):
    """A finished plan stops its Plan agent and records its session cost; a solo plan's clean worktree is merged."""

    def __init__(self, agents: PlanAgents, plans: Plans, branches: PlanBranchMerge) -> None:
        self.agents, self.plans, self.branches = agents, plans, branches

    def handle(self, event: PlanFinished) -> None:
        self.agents.stopped(event.plan_id)
        plan = self.plans.find(event.plan_id)
        if self.agents.is_on() and plan.mode == PlanMode.SOLO:
            self.branches.merge(event.plan_id)
