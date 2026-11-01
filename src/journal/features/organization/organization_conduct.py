from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.role_taken import RoleTaken
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.stop import Stop
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_reopened import TaskReopened
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.organization_part import OrganizationPart
from journal.features.organization.states.role_work import RoleWork


class OrganizationConduct(Conduct):
    """The organization feature's conduct in every state: a Role taken on is pushed as the state of working as it, with its guidance."""

    def on_role_taken(self, event: RoleTaken, settings: Settings) -> Transition:
        contracts = event.data.part(OrganizationPart).contracts
        work = RoleWork(role=event.role, version=contracts.version, task_id=event.task_id)
        return self.push(work, *work.guidance(contracts))

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        return self.none(*(nudge for nudge in (
            OrganizationConduct.unread_handoff(event), OrganizationConduct.waiting_handoff(event),
        ) if nudge), *OrganizationConduct.role_work_awaiting_check(event),
                          *OrganizationConduct.checked_parts_waiting_for_merge(event),
                          *OrganizationConduct.split_guidance(event))

    def on_task_reopened(self, event: TaskReopened, settings: Settings) -> Transition:
        progress = event.data.part(OrganizationPart).split_parts
        nudges = tuple(
            OrganizationNudges.SPLIT_PART_READY.create(task=part, role=role)
            for split in progress for part, role in split.ready_parts() if part == event.task_id
        )
        return self.none(*nudges)

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        progress = next(
            (split for split in event.data.part(OrganizationPart).split_parts if event.task_id in split.part_ids),
            None,
        )
        if progress is None:
            return self.none()
        if progress.all_completed():
            return self.none(OrganizationNudges.SPLIT_TASK_COMPLETED.create(task=progress.parent_id))
        if progress.all_cancelled():
            return self.none(OrganizationNudges.SPLIT_ALL_PARTS_CANCELLED.create(task=progress.parent_id))
        return self.none()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        if waiting := event.data.part(OrganizationPart).role_work_waiting_for_check:
            worker, task = waiting[0]
            return self.refuse(OrganizationNudges.ROLE_WORK_AWAITS_CHECK.create(worker=worker, task=task))
        if nudge := OrganizationConduct.unread_handoff(event):
            return self.refuse(nudge)
        nudge = OrganizationConduct.waiting_handoff(event)
        return self.refuse(nudge) if nudge else self.none()

    @staticmethod
    def unread_handoff(event: AgentEvent) -> Nudge | None:
        return OrganizationNudges.UNREAD_HANDOFF.create() if event.data.part(OrganizationPart).unread_handoff else None

    @staticmethod
    def waiting_handoff(event: AgentEvent) -> Nudge | None:
        waiting = event.data.part(OrganizationPart).waiting_plan_handoff
        if waiting is None:
            return None
        task, domain = waiting
        return OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF.create(task=task, domain=domain)

    @staticmethod
    def role_work_awaiting_check(event: AgentEvent) -> tuple[Nudge, ...]:
        return tuple(
            OrganizationNudges.ROLE_WORK_AWAITS_CHECK.create(worker=worker, task=task)
            for worker, task in event.data.part(OrganizationPart).role_work_waiting_for_check
        )

    @staticmethod
    def checked_parts_waiting_for_merge(event: AgentEvent) -> tuple[Nudge, ...]:
        return tuple(
            OrganizationNudges.SPLIT_PART_WAITING_FOR_MERGE.create(worker=worker, task=task)
            for worker, task in event.data.part(OrganizationPart).checked_parts_waiting_for_merge
        )

    @staticmethod
    def split_guidance(event: AgentEvent) -> tuple[Nudge, ...]:
        data = event.data.part(OrganizationPart)
        guidance = [
            OrganizationNudges.TASK_CAN_BE_SPLIT.create(task=task, domain=domain)
            for task, domain in data.split_tasks
        ]
        guidance.extend(
            OrganizationNudges.SPLIT_PART_READY.create(task=task, role=role)
            for split in data.split_parts for task, role in split.ready_parts()
        )
        guidance.extend(
            OrganizationNudges.SPLIT_ALL_PARTS_CANCELLED.create(task=split.parent_id)
            for split in data.split_parts if split.all_cancelled()
        )
        return tuple(guidance)
