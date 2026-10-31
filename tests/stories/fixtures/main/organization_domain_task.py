from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


class OrganizationDomainTask(OrganizationHubPlan):
    """An organization plan task already handed to its Domain seat."""

    parent = OrganizationHubPlan
    settings = ()

    def steps(self, story) -> None:
        story.agent_runs_from_organization_seat(
            story.agents.main,
            "plan",
            f"organization handoff {self.tasks.first} domain:alpha",
        ).expect_command_passed()
