from pathlib import Path

from journal.features.plans.plans_options import PlansOptions
from journal.features.workers.organization_options import OrganizationOptions
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


class OrganizationSharedRolePlanDraft(OrganizationHubPlan):
    """A draft plan with a task in Alpha and the shared Role contract."""

    parent = OrganizationHubPlan
    settings = (
        (OrganizationOptions.FOLDER, str(Path(__file__).with_name("organization_shared_role"))),
        (PlansOptions.PLAN_AGENTS, True),
    )
    task_domain = "alpha"
