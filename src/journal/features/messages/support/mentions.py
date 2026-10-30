import re

from journal.models.support.ref import Ref

NOUNS = "task|todo|plan|doc|document|report|message|template|sequence|trigger|check|question|memory|rule|reminder|worker|secret|phase"
TABLES = {"todo": "tasks", "document": "docs"}
PATTERN = re.compile(rf"\b({NOUNS})s?\s+#?(\d+)\b", re.IGNORECASE)


class Mentions:
    """The rows a text names: plan 1 is plans:1 and task 12 is tasks:12, in the order named, each once."""

    @staticmethod
    def found(text: str) -> list[Ref]:
        rows = []
        for type_name, n in PATTERN.findall(text):
            ref = Ref(TABLES.get(type_name.lower(), f"{type_name.lower()}s"), int(n))
            if ref not in rows:
                rows.append(ref)
        return rows
