from journal.engine.support.lazy_facts import LazyFacts
from journal.features.plans.support.phase_testing import PhaseTesting
from journal.features.plans.support.plan_statuses import PlanStatuses
from journal.features.plans.support.plan_testing import PlanTesting
from journal.features.plans.support.review_rounds import ReviewRounds
from journal.models.agent import Agent
from journal.models.plan import Plan
from journal.features.templates.shipped import PLAN_PHASE_TESTS, PLAN_ZERO_TESTS
from journal.repositories.entries import Entries
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.features.plans.support.plan_task_assigner import PlanTaskAssigner
from journal.features.tasks.support.task_briefing import TaskBriefing
from journal.features.plans.plans_nudges import PlansNudges
from journal.support.stage_times import StageTimes

EMPTY_PLAN_NOTE = "it has no brief and nothing logged yet"
# a task event is told after its task is written, so the task it names is the newest changed of its plan's
RECENT_PLAN_TASKS = 3


class PlansDataReader:
    """Reads the plans feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields PlansData names; a helper, whose file turns no plans on, never reads it; the started plan's facts the same, with the fields StartedPlan names."""

    def __init__(self, plans: Plans, briefing: TaskBriefing, entries: Entries, testing: PlanTesting, statuses: PlanStatuses, phase_testing: PhaseTesting, scope: Scope, stages: StageTimes, rounds: ReviewRounds, assigner: PlanTaskAssigner) -> None:
        self.plans, self.briefing, self.entries, self.testing, self.statuses, self.phase_testing = plans, briefing, entries, testing, statuses, phase_testing
        self.scope, self.stages, self.rounds, self.assigner = scope, stages, rounds, assigner

    def read(self, agent: Agent) -> LazyFacts:
        return LazyFacts("plans", {
            "approved": lambda: tuple(p.row_id for p in self.plans.approved()),
            "started": lambda: self.started(),
            "started_plans": lambda: self.statuses.started(),
            "review_reports": lambda: self.review_reports(),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)

    def started(self) -> LazyFacts | None:
        started = next(iter(self.plans.running_plans()), None)
        return self.started_plan(started) if started else None

    def review_reports(self) -> tuple[int, ...]:
        review = next(iter(self.plans.reviewed()), None)
        return tuple(report.row_id for report in self.rounds.unread(review)) if review else ()

    def started_plan(self, plan: Plan) -> LazyFacts:
        facts = LazyFacts("plans started", {
            "plan_id": lambda: plan.row_id,
            "next_task": lambda: self.next_task(plan),
            "has_next_task": lambda: self.plans.has_resumable(plan),
            "started_task": lambda: self.started_task(plan),
            "started_task_briefing": lambda: self.briefing_text(plan),
            "recent_tasks": lambda: tuple(self.plans.recent_task_ids(plan, RECENT_PLAN_TASKS)),
            "remaining_tasks": lambda: self.plans.remaining_count(plan),
            "checkpoint_pause": lambda: facts.is_checkpoint or bool(facts.phase_commands),
            "checkpoint_phase": lambda: self.checkpoint_phase(plan),
            "testing": lambda: " ".join(template.brief for template in self.testing.chosen(plan)),
            "phase_commands": lambda: self.phase_testing.unpassed(plan),
            "is_checkpoint": lambda: self.plans.checkpoint_plans(plan) is not None,
            "passes_checkpoints": lambda: self.assigner.passes_checkpoints(),
            "current_phase": lambda: plan.current_phase(self.plans.phase_states(plan)),
            "priorities_phase": lambda: plan.priorities_phase,
            "priorities_at": lambda: plan.priorities_at,
            "refuses_test_runs": lambda: self.refuses_test_runs(plan, facts.checkpoint_pause),
        }, lambda: self.scope.environment(plan.environment_id), self.stages)
        return facts

    def refuses_test_runs(self, plan: Plan, pausing: bool) -> bool:
        titles = {template.title for template in self.testing.chosen(plan)}
        if PLAN_ZERO_TESTS.title in titles:
            return True
        return PLAN_PHASE_TESTS.title in titles and not pausing and self.is_mid_phase(plan)

    def is_mid_phase(self, plan: Plan) -> bool:
        phases = self.plans.phase_states(plan)
        if not phases:
            return False
        current = phases[plan.current_phase(phases) - 1]
        return current.open_count() > 1 and current.has_work_completed()

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
        ended = self.plans.checkpoint_plans(plan) or self.plans.ended_phase(plan)
        return ended.number if ended is not None else 0
