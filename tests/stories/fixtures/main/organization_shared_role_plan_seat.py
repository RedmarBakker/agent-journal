from pathlib import Path

from journal.features.workers.organization_options import OrganizationOptions
from journal.features.plans.plans_options import PlansOptions
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.main.organization_plan_seat import OrganizationPlanSeat


class OrganizationSharedRolePlanSeat(OrganizationPlanSeat):
    """An organization plan uses a project with shared Roles."""

    parent = NewSession
    settings = (
        (OrganizationOptions.FOLDER, str(Path(__file__).with_name("organization_shared_role"))),
        (PlansOptions.PLAN_AGENTS, True),
    )
