from journal.features.organization.support.seat_runtime import SeatRuntime
from tests.lab.simulated_seats import SimulatedSeats
from tests.stories.fixtures.main.paused_organization_hub_plan import PausedOrganizationHubPlan


class StoppedOrganizationHubPlan(PausedOrganizationHubPlan):
    """An approved organization plan whose existing OpenRig rig has already stopped."""

    parent = PausedOrganizationHubPlan
    settings = ()

    def steps(self, story) -> None:
        story.openrig = SimulatedSeats()
        runtime = story.app.container.get(SeatRuntime)
        story.monkeypatch.setattr(runtime, "execute", story.openrig.execute)
        rig = f"plan-{self.plans.first}"
        story.openrig.rigs.add(rig)
        story.openrig.remember_spec(rig, runtime.spec_folder(rig) / "rig.yaml")
        story.openrig.run("down", rig, "--yes", "--json")
        story.observed(f"OpenRig stops {rig}", None, None)
