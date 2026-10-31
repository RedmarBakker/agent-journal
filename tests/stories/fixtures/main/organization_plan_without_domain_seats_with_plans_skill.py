from journal.features.skills.skills_options import SkillsOptions
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from tests.stories.fixtures.main.organization_plan_seat import OrganizationPlanSeat
from tests.stories.fixtures.main.organization_plan_without_domain_seats import OrganizationPlanWithoutDomainSeats


class OrganizationPlanWithoutDomainSeatsWithPlansSkill(OrganizationPlanWithoutDomainSeats):
    """An organization plan starts with the plans skill required in its environment."""

    parent = OrganizationPlanSeat
    settings = (
        (WorkersOptions.MODE, ORCHESTRATOR_MODE),
        (SkillsOptions.START_SKILLS, [*SkillsOptions.START_SKILLS.default, "plans"]),
    )
