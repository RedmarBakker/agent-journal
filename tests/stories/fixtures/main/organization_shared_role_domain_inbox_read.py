from tests.stories.fixtures.main.organization_shared_role_domain_seat_started import OrganizationSharedRoleDomainSeatStarted


class OrganizationSharedRoleDomainInboxRead(OrganizationSharedRoleDomainSeatStarted):
    """The shared-Role Domain seat has read its plan task from the inbox."""

    parent = OrganizationSharedRoleDomainSeatStarted

    def steps(self, story) -> None:
        domain = story.organization_seat_agent("domain:alpha")
        result = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
        result.expect_command_passed()
