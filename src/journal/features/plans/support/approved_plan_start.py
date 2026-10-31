from journal.features.plans.support.phase_testing import PhaseTesting
from journal.features.estimates.support.work_in_progress import WorkInProgress
from journal.features.workers.support.work_mode import WorkMode
from journal.models.agent import Agent
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.repositories.agents import Agents
from journal.repositories.plans import Plans
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor


class ApprovedPlanStart:
    """Starts the oldest approved plan for the agent here, in the orchestrator's mode without a task and otherwise with its first task in hand, when no plan is started, its testing allows it and the agent has no task in progress; with no agent here it starts none."""

    def __init__(self, plans: Plans, agents: Agents, tasks: Tasks, orchestrator: WorkMode,
                 testing: PhaseTesting, flow: WorkInProgress) -> None:
        self.plans, self.agents, self.tasks = plans, agents, tasks
        self.orchestrator, self.testing, self.flow = orchestrator, testing, flow

    def run(self) -> None:
        present = self.agents.current()
        if present is None:
            return
        if self.orchestrator.delegates_work():
            self.opened()
        else:
            self.started(present)

    def startable(self) -> Plan | None:
        approved = self.plans.approved()
        if self.plans.running_plans() or not approved or self.testing.refusal(approved[0]):
            return None
        return approved[0]

    def opened(self) -> None:
        plan = self.startable()
        if plan is not None:
            self.plans.opened(plan, Actor.system())

    def started(self, agent: Agent) -> Plan | None:
        with self.tasks.writing():
            plan = self.startable()
            current = self.tasks.holder_task(Ref.build(agent))
            if plan is None or (current is not None and current.is_started()):
                return None
            task = self.plans.following_task(plan)
            if task is not None and self.flow.block_reason(task):
                return None
            return self.plans.start(plan, Ref.build(agent), Actor.system())
