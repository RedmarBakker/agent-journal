from tests.stories.fixtures.main.paused_organization_hub_plan import PausedOrganizationHubPlan


class StoppedOrganizationHubPlan(PausedOrganizationHubPlan):
    """An approved organization plan whose existing OpenRig rig has already stopped."""

    def steps(self, story) -> None:
        super().steps(story)
        story.openrig.run("down", f"plan-{self.plans.first}", "--yes", "--json")
