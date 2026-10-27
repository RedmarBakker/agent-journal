from journal.engine.conduct import Conduct
from journal.events.rows.plan_testing_changed import PlanTestingChanged
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.drive_ended import DriveEnded
from journal.events.rows.plan_approved import PlanApproved
from journal.events.rows.plan_blocked import PlanBlocked
from journal.events.rows.plan_reopened import PlanReopened
from journal.events.rows.plan_reviewed import PlanReviewed
from journal.events.rows.plan_started import PlanStarted
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_started import TaskStarted
from journal.events.agent.tool_starting import ToolStarting
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.naming_test_commands import NamingTestCommands
from journal.features.shell.support.reader_commands import ReaderCommands
from journal.features.plans.plans_part import PlansPart
from journal.features.plans.support.started_plan import StartedPlan


class PlansConduct(Conduct):
    """The plans feature's conduct in every state: the user's approval informed, a drive of a hub row lost informed, a plan blocked or open again informed, the plan's next task named when the plan starts it, the wait named when none can start, at a start or a close, the plan's testing template informed when it starts and after each of its tasks closes, and a plan whose reviewers are all back instructed to be written into and readied."""

    def on_plan_approved(self, event: PlanApproved, settings: Settings) -> Transition:
        if not event.user_origin:
            return self.none()
        if event.comment_id is None:
            return self.none(PlansNudges.PLAN_APPROVED.create(n=event.plan_id))
        return self.none(PlansNudges.PLAN_APPROVED_WITH_COMMENT.create(n=event.plan_id, comment=event.comment_id))

    def on_plan_reviewed(self, event: PlanReviewed, settings: Settings) -> Transition:
        return self.none(PlansNudges.REVIEW_ENTRY_REQUEST.create(n=event.plan_id, reports=PlansNudges.unread(event.data.part(PlansPart).review_reports)))

    def on_plan_blocked(self, event: PlanBlocked, settings: Settings) -> Transition:
        return self.none(PlansNudges.PLAN_BLOCKED.create(n=event.plan_id, why=event.reason))

    def on_drive_ended(self, event: DriveEnded, settings: Settings) -> Transition:
        return self.none(PlansNudges.DRIVE_ENDED.create(name=event.name, why=event.reason, noun=event.noun, n=event.row_id))

    def on_plan_reopened(self, event: PlanReopened, settings: Settings) -> Transition:
        return self.none(PlansNudges.PLAN_REOPENED.create(n=event.plan_id, why=event.reason))

    def on_plan_started(self, event: PlanStarted, settings: Settings) -> Transition:
        started = event.data.part(PlansPart).started
        if started is None:
            return self.none()
        testing = testing_lines(started)
        if event.task_id or not started.remaining_tasks:
            return self.none(*testing)
        return self.none(*testing, PlansNudges.PLAN_STALLED.create(n=event.plan_id, left=started.remaining_tasks))

    def on_plan_testing_changed(self, event: PlanTestingChanged, settings: Settings) -> Transition:
        return self.none(PlansNudges.PLAN_TESTING_CHANGED.create(n=event.plan_id, template=event.title, testing=event.testing))

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        started = event.data.part(PlansPart).started
        if not is_started_plan_task(event, started):
            return self.none()
        lines = next_task_lines(event, started)
        return self.none(*lines) if test_commands(settings).programs else self.push(NamingTestCommands(task_id=event.task_id), *lines)

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if not event.call.test_runs() and not any(test_commands(settings).reads(part.text) for part in event.call.parts):
            return self.none()
        started = event.data.part(PlansPart).started
        if started is None or not started.refuses_test_runs:
            return self.none()
        return self.refuse(PlansNudges.MID_PHASE_TESTS.create(n=started.plan_id, phase=started.current_phase))

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        started = event.data.part(PlansPart).started
        if started is None or event.task_id not in started.recent_tasks:
            return self.none()
        testing = testing_lines(started)
        if started.started_task or started.has_next_task or started.checkpoint_pause or not started.remaining_tasks:
            return self.none(*testing)
        return self.none(*testing, PlansNudges.PLAN_STALLED.create(n=started.plan_id, left=started.remaining_tasks))


def test_commands(settings: Settings) -> ReaderCommands:
    return ReaderCommands.parsed(str(settings.value(PlansOptions.TEST_COMMANDS)))


def testing_lines(started: StartedPlan) -> tuple[Nudge, ...]:
    return (PlansNudges.PLAN_TESTING.create(n=started.plan_id, testing=started.testing),) if started.testing else ()


def next_task_lines(event: TaskStarted, started: StartedPlan | None) -> tuple[Nudge, ...]:
    if not event.plan_id or event.is_agents(event.session):
        return ()
    briefing = started.started_task_briefing if started else ""
    return (PlansNudges.NEXT_PLAN_TASK.create(n=event.plan_id, task=event.task_id, title=event.title, briefing=briefing),)


def is_started_plan_task(event: TaskStarted, started: StartedPlan | None) -> bool:
    return started is not None and started.started_task == event.task_id
