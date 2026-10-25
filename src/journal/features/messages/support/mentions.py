import re

from journal.models.support.ref import Ref

NOUNS = "task|todo|plan|doc|document|report|message|template|sequence|trigger|check|question|fact|rule|reminder|worker|secret|phase"
TABLES = {"todo": "tasks", "document": "docs"}


class Mentions:
    """The rows a text names: plan 1 is plans:1, task 12 is tasks:12, and acme plan 12 is team/plans:12 for a team named acme whose hub environment is named team. In the order named, each once."""

    @staticmethod
    def found(text: str, teams: list[str] = (), hub: str = "") -> list[Ref]:
        rows = []
        for team, kind, n in Mentions.pattern(teams).findall(text):
            table = TABLES.get(kind.lower(), f"{kind.lower()}s")
            ref = Ref(f"{hub}/{table}" if team else table, int(n))
            if ref not in rows:
                rows.append(ref)
        return rows

    @staticmethod
    def pattern(teams: list[str]) -> re.Pattern:
        named = "|".join(re.escape(team) for team in teams if team)
        team = rf"(?:\b({named})\s+)?" if named else "()"
        return re.compile(rf"{team}\b({NOUNS})s?\s+#?(\d+)\b", re.IGNORECASE)
