from journal.events.listener import Listener
from journal.events.rows.plan_reviewed import PlanReviewed
from journal.features.sequences.support.run_tracker import RunTracker
from journal.models.plan import Plan
from journal.repositories.agents import Agents
from journal.repositories.sequences import Sequences
from journal.supervisor_link import SupervisorLink

REVIEWED = "plan.reviewed"


class ReviewedPlanStart(Listener[PlanReviewed]):
    """A plan whose reviewers are all back starts the sequence that names that moment, Applying a plan's reviews, for the environment's main agent, about the plan; its first step is typed to the agent."""

    def __init__(self, sequences: Sequences, agents: Agents, active: RunTracker, supervisor: SupervisorLink) -> None:
        self.sequences, self.agents, self.running, self.supervisor = sequences, agents, active, supervisor

    def handle(self, event: PlanReviewed) -> None:
        mains = self.agents.main_scoped(event.environment_id)
        for sequence in self.sequences.triggered_sequences(REVIEWED)[:1] if mains else ():
            line = self.running.start(sequence, mains[-1].session, event.environment_id, topic=f"{Plan.table()}:{event.plan_id}")
            if line and self.running.typed_agent(mains[-1].session, event.environment_id):
                self.supervisor.type(event.environment_id, line)
