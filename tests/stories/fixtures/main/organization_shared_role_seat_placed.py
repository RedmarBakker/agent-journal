from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.providers.providers import Providers
from journal.repositories.plans import Plans
from tests.stories.fixtures.main.organization_shared_role_domain_inbox_read import OrganizationSharedRoleDomainInboxRead


class OrganizationSharedRoleSeatPlaced(OrganizationSharedRoleDomainInboxRead):
    """The shared Role seat is placed before its writing worker exists."""

    parent = OrganizationSharedRoleDomainInboxRead
    settings = ()

    def steps(self, story) -> None:
        plan = story.app.container.get(Plans).global_matching(id=self.plans.first)[0]
        organization = story.app.container.get(Organization).reload()
        role = organization.role("shared")
        provider = story.app.container.get(Providers).lookup(story.provider)
        story.app.container.get(RigStaffing).shared_read_only_role_rig(
            plan, organization, role, provider.name,
        )
