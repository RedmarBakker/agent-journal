import argparse
from collections.abc import Callable


class RoleVerbs:
    """A noun's verbs as one agent role sees them: every verb parses, so a refusal can name what the role may run, and help and usage show only the verbs it may run, since a verb added with no help is left out of the listing."""

    def __init__(self, verbs, allowed: Callable[[str], bool]) -> None:
        self.verbs, self.allowed = verbs, allowed
        self.shown: list[str] = []

    def add_parser(self, name: str, **settings) -> argparse.ArgumentParser:
        if self.allowed(name):
            self.shown.append(name)
            self.verbs.metavar = "{" + ",".join(self.shown) + "}"
            return self.verbs.add_parser(name, **settings)
        return self.verbs.add_parser(name, **{key: value for key, value in settings.items() if key != "help"})
