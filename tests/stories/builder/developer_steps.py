import json

from journal.features.faults.support.story_transitions import StoryTransitions


class DeveloperSteps:
    """What a developer of the journal brings to a story: the kinds of stack change the last full story run walked, as that run writes them."""

    def story_run_walked(self, *kinds: str) -> None:
        walked_path = StoryTransitions.walked_path(self.app.config)
        walked_path.parent.mkdir(parents=True, exist_ok=True)
        walked_path.write_text(json.dumps(list(kinds)))
        self.observed(f"the last story run walked {len(kinds)} kinds", None, None)
