from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.role_taken import RoleTaken
from journal.features.organization.organization_part import OrganizationPart
from journal.features.organization.states.role_work import RoleWork


class OrganizationConduct(Conduct):
    """The organization feature's conduct in every state: a Role taken on is pushed as the state of working as it, with its guidance."""

    def on_role_taken(self, event: RoleTaken, settings: Settings) -> Transition:
        contracts = event.data.part(OrganizationPart).contracts
        work = RoleWork(role=event.role, version=contracts.version, task_id=event.task_id)
        return self.push(work, *work.guidance(contracts))
