from journal.events.listener import Listener
from journal.events.rows.plan_finished import PlanFinished
from journal.features.plans.support.plan_agents import PlanAgents
from journal.features.plans.support.plan_branch_merge import PlanBranchMerge
from journal.models.author import Author
from journal.models.message import Message
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.repositories.environments import Environments
from journal.repositories.messages import Messages
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.rejection import Rejection


class PlanAgentFinish(Listener[PlanFinished]):
    """A finished plan stops its Plan agent and records its session cost; a solo plan's worktree is merged and failures reach both chats."""

    def __init__(self, agents: PlanAgents, plans: Plans, branches: PlanBranchMerge, environments: Environments, messages: Messages, scope: Scope) -> None:
        self.agents, self.plans, self.branches, self.environments, self.messages, self.scope = agents, plans, branches, environments, messages, scope

    def handle(self, event: PlanFinished) -> None:
        with self.scope.environment(event.environment_id):
            plan = self.plans.find(event.plan_id)
            self.agents.stopped(event)
            if self.agents.is_on() and plan.mode == PlanMode.SOLO:
                try:
                    self.branches.merge(event.plan_id)
                except Rejection as reason:
                    self.report_failure(plan, str(reason))

    def report_failure(self, plan: Plan, reason: str) -> None:
        starting = self.environments.find(plan.environment_id)
        plan_environment = self.agents.environment(plan)
        recipients = [self.environments.existing("main").row_id, plan.environment_id]
        if plan_environment:
            recipients.append(plan_environment.row_id)
        text = (
            f"Plan {plan.id} branch merge failed: {reason}. Review the named files in the plan worktree and {starting.name}, "
            f"resolve the issue, then run `journal plan merge {plan.id}` in {starting.name}."
        )
        for environment_id in dict.fromkeys(recipients):
            with self.scope.environment(environment_id):
                self.messages.save(Message(
                    environment_id=environment_id,
                    author=Author.SYSTEM,
                    text=text,
                    data={"kind": "plan_merge_failure", "plan": plan.id},
                ), Actor.system())
