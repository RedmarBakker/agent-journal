from tests.stories.fixtures.main.supervisor_owner_action import (
    SupervisorOwnerAction,
    SupervisorOwnerActionSetup,
    seed_owner_action,
)


class SupervisorOwnerTierTwoAction(SupervisorOwnerAction):
    """A plan owner has a recorded tier two supervisor action to undo."""

    parent = SupervisorOwnerActionSetup

    def steps(self, story) -> None:
        self._owner_action = seed_owner_action(story, self._owner_action_setup, "tier 2")
