from tests.stories.fixtures.main.organization_plan_without_domain_seats import OrganizationPlanWithoutDomainSeats
from tests.stories.fixtures.main.organization_shared_role_plan_seat import OrganizationSharedRolePlanSeat


class OrganizationSharedRolePlanWithoutDomainSeats(OrganizationPlanWithoutDomainSeats):
    """A shared-Role organization plan has started and has no Domain seats."""

    parent = OrganizationSharedRolePlanSeat
    settings = ()
