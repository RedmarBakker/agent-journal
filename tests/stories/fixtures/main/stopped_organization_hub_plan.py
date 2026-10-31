from journal.features.organization.support.seat_runtime import SeatRuntime
from tests.stories.fixtures.main.paused_organization_hub_plan import PausedOrganizationHubPlan


class StoppedOrganizationHubPlan(PausedOrganizationHubPlan):
    """An approved organization plan whose existing OpenRig rig has already stopped."""

    parent = PausedOrganizationHubPlan
    settings = ()

    def steps(self, story) -> None:
        story.configure_simulated_openrig()
        runtime = story.app.container.get(SeatRuntime)
        rig = story.plan_rig_name(self.plans.first)
        story.openrig.rigs.add(rig)
        story.openrig.remember_spec(rig, runtime.spec_folder(rig) / "rig.yaml")
        story.openrig.run("down", rig, "--yes", "--json")
        story.observed(f"OpenRig stops {rig}", None, None)
