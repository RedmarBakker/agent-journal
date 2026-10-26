from journal.features.plans.support.phase_testing import PhaseTesting
from journal.features.workers.support.orchestrator_mode import OrchestratorMode
from journal.models.support.ref import Ref
from journal.repositories.agents import Agents
from journal.repositories.plans import Plans
from journal.support.actor import Actor


class ApprovedPlanStart:
    """Starts the oldest approved plan, in the orchestrator's mode without a task and otherwise with its first task in hand, when no plan is started and its testing allows it."""

    def __init__(self, plans: Plans, agents: Agents, orchestrator: OrchestratorMode, testing: PhaseTesting) -> None:
        self.plans, self.agents, self.orchestrator, self.testing = plans, agents, orchestrator, testing

    def run(self) -> None:
        approved = self.plans.approved()
        if self.plans.running_plans() or not approved or self.testing.refusal(approved[0]):
            return
        plan, present = approved[0], self.agents.current()
        if self.orchestrator.is_set():
            self.plans.opened(plan, Actor.system())
        else:
            self.plans.start(plan, None if present is None else Ref.build(present), Actor.system())
