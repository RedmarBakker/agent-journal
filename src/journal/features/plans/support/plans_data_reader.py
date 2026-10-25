from journal.engine.support.lazy_facts import LazyFacts
from journal.features.plans.support.plan_statuses import PlanStatuses
from journal.features.plans.support.plan_testing import PlanTesting
from journal.models.agent import Agent
from journal.models.plan import Plan
from journal.repositories.entries import Entries
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.features.tasks.support.task_briefing import TaskBriefing
from journal.features.plans.plans_nudges import PlansNudges
from journal.support.stage_times import StageTimes

EMPTY_PLAN_NOTE = "it has no brief and nothing logged yet"
# a task event is told after its task is written, so the task it names is the newest changed of its plan's
RECENT_PLAN_TASKS = 3


class PlansDataReader:
    """Reads the plans feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields PlansData names; the started plan's facts the same, with the fields StartedPlan names."""

    def __init__(self, plans: Plans, briefing: TaskBriefing, entries: Entries, testing: PlanTesting, statuses: PlanStatuses, scope: Scope, stages: StageTimes) -> None:
        self.plans, self.briefing, self.entries, self.testing, self.statuses = plans, briefing, entries, testing, statuses
        self.scope, self.stages = scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        return LazyFacts("plans", {
            "approved": lambda: tuple(p.row_id for p in self.plans.approved()),
            "started": lambda: self.started(),
            "review_plan": lambda: self.review_plan(agent),
            "started_plans": lambda: self.statuses.started(),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)

    def started(self) -> LazyFacts | None:
        started = next(iter(self.plans.running_plans()), None)
        return self.started_plan(started) if started else None

    def review_plan(self, agent: Agent) -> int:
        review = next(iter(self.plans.reviewed()), None)
        review_line = self.entries.last_line_entry(agent.session, (PlansNudges.REVIEW_ENTRY_REQUEST.key,)) if review else None
        return review.row_id if review_line else 0

    def started_plan(self, plan: Plan) -> LazyFacts:
        return LazyFacts("plans started", {
            "plan_id": lambda: plan.row_id,
            "next_task": lambda: self.next_task(plan),
            "started_task": lambda: self.started_task(plan),
            "started_task_briefing": lambda: self.briefing_text(plan),
            "recent_tasks": lambda: tuple(self.plans.recent_task_ids(plan, RECENT_PLAN_TASKS)),
            "remaining_tasks": lambda: self.plans.remaining_count(plan),
            "checkpoint_pause": lambda: self.plans.checkpoint_plans(plan) is not None,
            "checkpoint_phase": lambda: self.checkpoint_phase(plan),
            "testing": lambda: " ".join(template.brief for template in self.testing.chosen(plan)),
        }, lambda: self.scope.environment(plan.environment_id), self.stages)

    def next_task(self, plan: Plan) -> int:
        task = self.plans.resumable(plan)
        return task.row_id if task else 0

    def started_task(self, plan: Plan) -> int:
        current = self.plans.started_task(plan)
        return current.row_id if current else 0

    def briefing_text(self, plan: Plan) -> str:
        current = self.plans.started_task(plan)
        return (self.briefing.text(current) or EMPTY_PLAN_NOTE) if current else ""

    def checkpoint_phase(self, plan: Plan) -> int:
        checkpoint = self.plans.checkpoint_plans(plan)
        return checkpoint.number if checkpoint is not None else 0
