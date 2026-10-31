from journal.features.organization.support.organization import Organization
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.support.ref import Ref
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from tests.lab.simulated_seats import SimulatedSeats
from tests.stories.fixtures.main.organization_plan_handoff_seat import OrganizationPlanHandoffSeat


class OrganizationDomainTaskWithEndedRoleWorker(OrganizationPlanHandoffSeat):
    """A Domain has an unread task handoff held by an ended Role worker."""

    parent = OrganizationPlanHandoffSeat

    def steps(self, story) -> None:
        story.monkeypatch.setattr(WorkerRunner, "start", story.app.original_worker_start)
        story.openrig = SimulatedSeats()
        story.monkeypatch.setattr(story.app.container.get(SeatRuntime), "execute", story.openrig.execute)
        task = self.tasks.first
        plan = story.app.container.get(Plans).global_matching(id=self.plans.first)[0]
        handoff = story.agent_runs_from_plan_organization_seat(
            story.agents.main, "plan", f"organization handoff {task} domain:alpha",
        )
        handoff.expect_command_passed()
        organization = story.app.container.get(Organization)
        contracts = organization.contracts()
        role = contracts.role("builder")
        with story.app.container.get(Scope).environment(plan.environment_id):
            task_row = story.app.container.get(Tasks).find(task)
            worker = Worker(
                environment_id=plan.environment_id,
                name="Earlier organization writer",
                brief="The earlier run ended without clocking out.",
                provider=story.provider,
                model=role.models.for_provider(story.provider),
                role=role.id,
                contract=contracts.version,
                plan_id=plan.row_id,
            )
            workers = story.app.container.get(Workers)
            worker = workers.save(worker, Actor.system())
            ended_at = story.app.container.get(TimeSource).seconds()
            worker = workers.save(worker.unfinished(ended_at, "ended without clocking out"), Actor.system())
            story.app.container.get(Tasks).handover(task_row, Ref.build(worker), Actor.system())
        self.workers.first = worker.row_id

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN, delegated=True)
        story.expect_worker(self.workers.first, state=WorkerState.UNFINISHED)
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
