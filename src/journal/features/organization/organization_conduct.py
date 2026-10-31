from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.role_taken import RoleTaken
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.stop import Stop
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
        ) if nudge), *OrganizationConduct.role_work_awaiting_check(event))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
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
