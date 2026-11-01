from tests.stories.fixtures.main.organization_domain_seat_started import OrganizationDomainSeatStarted
from tests.stories.fixtures.main.organization_shared_role_plan_without_domain_seats import OrganizationSharedRolePlanWithoutDomainSeats


class OrganizationSharedRoleDomainSeatStarted(OrganizationDomainSeatStarted):
    """A shared-Role organization plan has handed its task to its Domain seat."""

    parent = OrganizationSharedRolePlanWithoutDomainSeats
    settings = ()
