from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.main.supervisor_owner_action import SupervisorOwnerAction, seed_owner_action


class SupervisorOwnerTierTwoAction(SupervisorOwnerAction):
    """A plan owner has a recorded supervisor plan-priorities action at tier 2."""

    parent = NewSession
    stack = (Ready,)

    def steps(self, story) -> None:
        self._owner_action = seed_owner_action(story, "tier 2")
