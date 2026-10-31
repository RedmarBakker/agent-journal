from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from tests.stories.fixtures.main.organization_plan_seat import OrganizationPlanSeat


class OrganizationPlanOrchestrator(OrganizationPlanSeat):
    """An approved organization plan with its worker mode set to orchestrator."""

    parent = OrganizationPlanSeat
    settings = ((WorkersOptions.MODE, ORCHESTRATOR_MODE),)

    def steps(self, story) -> None:
        return
