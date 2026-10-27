import re

NAME_LENGTH = 80


class LibraryName:
    """The name a row is published under when it has none of its own, from its title: lower case, every run of other characters one dash, no dash at either end, at most eighty characters, so the server's name rule takes it."""

    @staticmethod
    def from_title(title: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:NAME_LENGTH].strip("-")
