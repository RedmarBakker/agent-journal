from journal.features.feature import Feature
from journal.features.reviewing.commands.review_command import ReviewCommand
from journal.features.reviewing.listeners.review_handback import ReviewHandback
from journal.features.reviewing.listeners.reviewer_retirement import ReviewerRetirement
from journal.features.reviewing.listeners.reviewer_start import ReviewerStart
from journal.features.reviewing.reviewing_conduct import ReviewingConduct
from journal.features.reviewing.reviewing_nudges import ReviewingNudges
from journal.features.reviewing.reviewing_options import ReviewingOptions
from journal.features.reviewing.states.reviewing import Reviewing
from journal.models.agent_role import AgentRole


class ReviewingFeature(Feature):
    """In orchestrator mode with the reviewer on, a worker's clock-out goes to a reviewer the journal sends itself rather than to the agent that sent the worker: the reviewer is an agent of its own, never a worker, resting on Reviewing from its first hook; it reads the brief and each proof, runs the tests, judges the changes and reports each point, and the agent decides, sending the work back or merging it."""

    name = "reviewing"
    title = "Reviewing workers' work"
    fixed = True
    help = "In orchestrator mode with the reviewer on, the journal sends a reviewer to each worker that clocks out; its report on each point comes to the agent, which sends the work back or merges it."
    states = (Reviewing,)
    floors = {AgentRole.REVIEWER: Reviewing}
    options = (ReviewingOptions.REVIEWER,)
    commands = (ReviewCommand,)
    listeners = (ReviewerStart, ReviewHandback, ReviewerRetirement)
    conduct = (ReviewingConduct,)
    nudges = (ReviewingNudges.REVIEWER_WRITES, ReviewingNudges.REPORT_REQUEST, ReviewingNudges.WORK_REVIEWED, ReviewingNudges.REVIEW_FAILED)
