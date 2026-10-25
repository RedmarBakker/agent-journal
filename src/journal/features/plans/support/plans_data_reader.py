from journal.engine.support.lazy_facts import LazyFacts
from journal.features.plans.support.plan_testing import PlanTesting
from journal.features.plans.support.started_plan import StartedPlan
from journal.models.agent import Agent
from journal.models.plan import Plan
from journal.models.task_state import TaskState
from journal.repositories.entries import Entries
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.features.tasks.support.task_briefing import TaskBriefing
from journal.features.plans.plans_nudges import PlansNudges
from journal.support.stage_times import StageTimes

EMPTY_PLAN_NOTE = "it has no brief and nothing logged yet"


class PlansDataReader:
    """Reads the plans feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields PlansData names."""

    def __init__(self, plans: Plans, briefing: TaskBriefing, entries: Entries, testing: PlanTesting, scope: Scope, stages: StageTimes) -> None:
        self.plans, self.briefing, self.entries, self.testing = plans, briefing, entries, testing
        self.scope, self.stages = scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        return LazyFacts("plans", {
            "approved": lambda: tuple(p.row_id for p in self.plans.approved()),
            "started": lambda: self.started(),
            "review_plan": lambda: self.review_plan(agent),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)

    def started(self) -> StartedPlan | None:
        started = next(iter(self.plans.running_plans()), None)
        return self.started_plan(started) if started else None

    def review_plan(self, agent: Agent) -> int:
        review = next(iter(self.plans.reviewed()), None)
        review_line = self.entries.last_line_entry(agent.session, (PlansNudges.REVIEW_ENTRY_REQUEST.key,)) if review else None
        return review.row_id if review_line else 0

    def started_plan(self, plan: Plan) -> StartedPlan:
        tree = self.plans.tree(plan)
        tasks = tree.tasks
        task = self.plans.resumable_task(tree)
        current = next((t for t in tasks if t.state == TaskState.STARTED), None)
        briefing = (self.briefing.text(current) or EMPTY_PLAN_NOTE) if current else ""
        checkpoint = plan.checkpoint_phase([phase.states() for phase in tree.phased])
        phase = checkpoint.number if checkpoint is not None else 0
        return StartedPlan(plan_id=plan.row_id, next_task=task.row_id if task else 0, started_task=current.row_id if current else 0, started_task_briefing=briefing, tasks=tuple(t.row_id for t in tasks), remaining_tasks=sum(1 for t in tasks if not t.is_closed()), checkpoint_pause=checkpoint is not None, checkpoint_phase=phase, testing=" ".join(template.brief for template in self.testing.chosen(plan)))
