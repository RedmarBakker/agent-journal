from journal.features.plans.support.plan_testing import PlanTesting
from journal.features.plans.support.review_rounds import ReviewRounds
from journal.http.support.model_fields import ModelFields
from journal.models.plan import Plan
from journal.repositories.messages import Messages
from journal.repositories.plan_reviews import PlanReviews
from journal.repositories.plans import Plans
from journal.repositories.tasks import Tasks


class PlanOutline:
    """A plan with its phases, each with its task numbers in order, the tasks under no phase, the phase in hand, whether it stands at a checkpoint for the user, whether a worker holds one of its tasks, the titles of the testing template it follows, its review rounds, newest first, each with the reports it filed, and how many comments are under it; read from its links and, for an open plan's phase in hand and checkpoint, its tasks' state counts, never its tasks' rows."""

    def __init__(self, plans: Plans, tasks: Tasks, reviews: PlanReviews, rounds: ReviewRounds, testing: PlanTesting) -> None:
        self.plans, self.tasks, self.reviews, self.rounds, self.testing = plans, tasks, reviews, rounds, testing

    def build(self, plan: Plan) -> dict:
        if plan.state.is_closed():
            return self.closed_outline(plan)
        return self.open_outline(plan)

    def open_outline(self, plan: Plan) -> dict:
        phased = self.plans.phase_states(plan)
        members = self.plans.phase_task_ids([phase.phase for phase in phased])
        phased_ids = list(dict.fromkeys(task_id for phase in phased for task_id in members[phase.phase.id]))
        task_ids = phased_ids + self.plans.unphased_task_ids(plan, phased_ids)
        phases = [{**ModelFields.build(phase.phase), "task_ids": members[phase.phase.id]} for phase in phased]
        checkpoint_pause = plan.is_started() and plan.checkpoint_phase(phased) is not None
        return self.outline(plan, task_ids, phases, plan.current_phase(phased), checkpoint_pause, self.tasks.has_worker_holder(task_ids))

    def closed_outline(self, plan: Plan) -> dict:
        phases = self.plans.plan_phases(plan)
        members = self.plans.phase_task_ids(phases)
        listed = [{**ModelFields.build(phase), "task_ids": members[phase.id]} for phase in phases]
        return self.outline(plan, self.plans.plan_task_ids(plan), listed, len(phases) or 1, False, False)

    def outline(self, plan: Plan, task_ids: list[int], phases: list[dict], current_phase: int, checkpoint_pause: bool, is_delegated: bool) -> dict:
        members = {n for phase in phases for n in phase["task_ids"]}
        return {**ModelFields.build(plan), "task_ids": task_ids, "phases": phases, "unphased_task_ids": [n for n in task_ids if n not in members],
                "current_phase": current_phase, "held": checkpoint_pause, "delegated": is_delegated, "testing": [template.title for template in self.testing.chosen(plan)],
                "reviews": [{**ModelFields.build(review), "report_ids": self.rounds.report_ids(review)} for review in self.reviews.reviews(plan)],
                "comment_count": self.plans.linking_counts(Messages.COMMENT_LINK, [plan.id]).get(plan.id, 0)}
