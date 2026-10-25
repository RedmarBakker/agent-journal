from journal.models.scoped import Scoped
from journal.repositories.environments import Environments


class RowLabels:
    """How a row is named in a line: task 57, and acme task 57 when it is a row of the hub environment of the team named acme."""

    def __init__(self, environments: Environments) -> None:
        self.environments = environments

    def name(self, noun: str, row: Scoped) -> str:
        team = next((hub.team_name for hub in self.environments.hubs() if hub.row_id == row.environment_id), "")
        return f"{team} {noun} {row.row_id}" if team else f"{noun} {row.row_id}"
