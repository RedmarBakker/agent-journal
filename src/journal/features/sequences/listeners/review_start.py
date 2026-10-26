from journal.events.listener import Listener
from journal.events.rows.plan_review_started import PlanReviewStarted
from journal.features.sequences.support.announced_starts import AnnouncedStarts
from journal.models.plan import Plan
from journal.repositories.agents import Agents
from journal.repositories.sequences import Sequences


class ReviewStart(Listener[PlanReviewStarted]):
    """A plan put into review starts the sequence that names that moment, Applying a plan's reviews, for the environment's main agent, about the plan; its first step is typed to the agent."""

    def __init__(self, sequences: Sequences, agents: Agents, starts: AnnouncedStarts) -> None:
        self.sequences, self.agents, self.starts = sequences, agents, starts

    def handle(self, event: PlanReviewStarted) -> None:
        mains = self.agents.main_scoped(event.environment_id)
        for sequence in self.sequences.triggered_sequences(PlanReviewStarted.moment)[:1] if mains else ():
            self.starts.start(sequence, mains[-1].session, event.environment_id, topic=f"{Plan.table()}:{event.plan_id}")
