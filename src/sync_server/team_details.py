from sync_server.db.team_detail_rows import TeamDetailRows

KEY = "key"
NAME = "name"


class TeamDetails:
    """What the team server knows of its team: its key, drawn when the server is made, and its name, which a team from before the library was given by its first journal and a new one does not have."""

    def __init__(self, rows: TeamDetailRows) -> None:
        self.rows = rows

    def key(self) -> str:
        return self.rows.value(KEY)

    def name(self) -> str:
        return self.rows.value(NAME)
