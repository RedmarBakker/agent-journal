from journal.models.scoped import Scoped
from journal.repositories.environments import Environments


class RowLabels:
    """How a row is named in a line: task 57, and acme task 57 when it is a row of the hub environment of the team named acme."""

    def __init__(self, environments: Environments) -> None:
        self.environments = environments

    def name(self, noun: str, row: Scoped) -> str:
        return f"{self.noun(noun, row.environment_id)} {row.row_id}"

    def noun(self, noun: str, environment_id: int) -> str:
        return self.hub_nouns(noun).get(environment_id, noun)

    def hub_nouns(self, noun: str) -> dict[int, str]:
        return {hub.row_id: f"{hub.team_name} {noun}" for hub in self.environments.hubs()}
