from tests.stories.fixtures.main.organization_shared_seats import OrganizationSharedSeats


class SharedOrganizationDomainSeatStarted(OrganizationSharedSeats):
    """The shared Domain seat has started beside the owner's session."""

    parent = OrganizationSharedSeats
    settings = ()

    def steps(self, story) -> None:
        rig = story.shared_rig_name(self.plans.first)
        domain = story.organization_seat_agent("domain:alpha", rig)
        story.agent_starts_organization_seat(domain, "domain:alpha", rig).expect_allowed(domain)
