from journal.models.environment import Environment
from journal.sync.agent_rows import AgentRows
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink

CACHE_SECONDS = 1.0


class RemoteAgents:
    """The agent bar rows of an environment another journal of the team hosts, as its host last sent them to the team server, asked at most once a second for each environment; none while the team server cannot be reached or does not know agent views yet."""

    def __init__(self, link: TeamServerLink) -> None:
        self.link = link
        self.cache: dict[str, AgentRows] = {}

    def rows(self, environment: Environment, request_at: float) -> list[dict]:
        entry = self.cache.get(environment.key)
        if entry and request_at - entry.updated_at < CACHE_SECONDS:
            return entry.rows
        rows = [{**row, "remote": True} for row in self.fetched(environment.key)]
        self.cache[environment.key] = AgentRows(rows, request_at)
        return rows

    def fetched(self, key: str) -> list[dict]:
        try:
            return self.link.agent_views([key]).get(key, [])
        except (OSError, TeamRefusal) as fault:
            print(f"the agent view of environment {key} could not be read from the team server: {fault}", flush=True)
            return []
