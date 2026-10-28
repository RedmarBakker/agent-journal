import json

from journal.features.faults.support.scenario_transitions import ScenarioTransitions


class DeveloperSteps:
    """What a developer of the journal brings to a story: the kinds of stack change the last full scenario run walked, as that run writes them."""

    def scenario_run_walked(self, *kinds: str) -> None:
        walked_path = ScenarioTransitions.walked_path(self.app.config)
        walked_path.parent.mkdir(parents=True, exist_ok=True)
        walked_path.write_text(json.dumps(list(kinds)))
        self.observed(f"the last scenario run walked {len(kinds)} kinds", None, None)
