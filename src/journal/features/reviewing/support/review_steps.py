from journal.chat.moment_cards import MomentCards
from journal.features.reviewing.support.review_point import BAD, GOOD
from journal.features.reviewing.support.review_report import ReviewReport
from journal.events.rows.worker_mention import WorkerMention
from journal.models.agent_role import AgentRole
from journal.models.reviewer import Reviewer
from journal.support.actor import Actor
from journal.support.card_kind import CardKind

REVIEW_STEP = "review_step"


class ReviewSteps:
    """What a reviewer does, shown in its own chat for the reviewer pane on Home, which nobody types in, by the listeners that hear each step: each review started, each test it ran and how it went, each point of its report passed or short, and the report it handed the agent."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def started(self, reviewer: Reviewer, worker: WorkerMention) -> None:
        self.step(reviewer.environment_id, reviewer.session, f"Started reviewing {worker.title()}", "")

    def test_passed(self, reviewer: Reviewer, command: str) -> None:
        self.step(reviewer.environment_id, reviewer.session, f"Ran {command}: passed", GOOD)

    def test_failed(self, reviewer: Reviewer, command: str) -> None:
        self.step(reviewer.environment_id, reviewer.session, f"Ran {command}: failed", BAD)

    def reported(self, environment_id: int, session: str, worker: WorkerMention, report: ReviewReport) -> None:
        for point in report.points():
            self.step(environment_id, session, point.line(), point.tone())
        self.step(environment_id, session, f"Handed its report on {worker.title()}, to the agent: {report.text}", "")

    def step(self, environment_id: int, session: str, text: str, tone: str) -> None:
        self.cards.show_role_card(AgentRole.REVIEWER, environment_id, session, text, {"kind": REVIEW_STEP, "icon": "reviewer", "tone": tone}, Actor.system(), CardKind.REVIEWERS)
