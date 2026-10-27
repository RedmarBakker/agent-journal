import re
from types import MappingProxyType

from journal.models.support.ref import Ref

NOUNS = "task|todo|plan|doc|document|report|message|template|sequence|trigger|check|question|memory|rule|reminder|worker|secret|phase"
TABLES = {"todo": "tasks", "document": "docs"}
NO_HUBS = MappingProxyType({})


class Mentions:
    """The rows a text names: plan 1 is plans:1, task 12 is tasks:12, and acme plan 12 is acme/plans:12 for a team named acme whose hub environment is named acme, each team's name mapped to its hub's. In the order named, each once."""

    @staticmethod
    def found(text: str, hubs: MappingProxyType = NO_HUBS) -> list[Ref]:
        named = {team.lower(): hub for team, hub in hubs.items()}
        rows = []
        for team, type_name, n in Mentions.pattern(list(hubs)).findall(text):
            table = TABLES.get(type_name.lower(), f"{type_name.lower()}s")
            ref = Ref(f"{named[team.lower()]}/{table}" if team else table, int(n))
            if ref not in rows:
                rows.append(ref)
        return rows

    @staticmethod
    def pattern(teams: list[str]) -> re.Pattern:
        named = "|".join(re.escape(team) for team in teams if team)
        team = rf"(?:\b({named})\s+)?" if named else "()"
        return re.compile(rf"{team}\b({NOUNS})s?\s+#?(\d+)\b", re.IGNORECASE)
