from journal.features.plans.support.phase_testing import PhaseTesting
from journal.features.workers.support.orchestrator_mode import OrchestratorMode
from journal.models.support.ref import Ref
from journal.repositories.agents import Agents
from journal.repositories.plans import Plans
from journal.support.actor import Actor


class ApprovedPlanStart:
    """Starts the oldest approved plan for the agent here, in the orchestrator's mode without a task and otherwise with its first task in hand, when no plan is started and its testing allows it; with no agent here it starts none."""

    def __init__(self, plans: Plans, agents: Agents, orchestrator: OrchestratorMode, testing: PhaseTesting) -> None:
        self.plans, self.agents, self.orchestrator, self.testing = plans, agents, orchestrator, testing

    def run(self) -> None:
        approved, present = self.plans.approved(), self.agents.current()
        if present is None or self.plans.running_plans() or not approved or self.testing.refusal(approved[0]):
            return
        if self.orchestrator.is_set():
            self.plans.opened(approved[0], Actor.system())
        else:
            self.plans.start(approved[0], Ref.build(present), Actor.system())
