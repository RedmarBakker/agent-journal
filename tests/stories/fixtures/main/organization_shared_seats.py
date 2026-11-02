from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.repositories.plans import Plans
from tests.stories.fixtures.main.organization_shared_role_plan_seat import OrganizationSharedRolePlanSeat


class OrganizationSharedSeats(OrganizationSharedRolePlanSeat):
    """An approved plan has a shared Domain and read-only Role seat beside its main agent."""

    parent = OrganizationSharedRolePlanSeat
    settings = ()

    def steps(self, story) -> None:
        plan = story.app.container.get(Plans).global_matching(id=self.plans.first)[0]
        contracts = story.app.container.get(Organization).contracts()
        story.app.container.get(RigStaffing).shared_read_only_role_rig(plan, contracts, contracts.role("shared"), story.provider)
        story.observed("the shared Domain and Role seats are placed", None, None)
