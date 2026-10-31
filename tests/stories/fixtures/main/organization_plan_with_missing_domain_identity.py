import json

from journal.features.organization.support.rig_specs import RigSpecs
from journal.support.caller import ORGANIZATION_SEAT
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats


class OrganizationPlanWithMissingDomainIdentity(OrganizationPlanWithDomainSeats):
    """A running organization plan has a Domain member without its seat identity."""

    parent = OrganizationPlanWithDomainSeats
    settings = ()

    def steps(self, story) -> None:
        path, spec = story.app.container.get(RigSpecs).read_rig_spec(f"plan-{self.plans.first}")
        member = next(
            member
            for pod in spec["pods"] if pod["id"] == "alpha"
            for member in pod["members"] if member["id"] == "domain-agent"
        )
        member["env"].pop(ORGANIZATION_SEAT)
        path.write_text(json.dumps(spec))
        story.observed("the generated Domain seat has no organization identity", None, None)
