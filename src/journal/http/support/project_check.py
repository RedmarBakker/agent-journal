from pathlib import Path

from journal.config import Config
from journal.support.response import Response

PROJECT_HEADER = "X-Journal-Project"
# the word a refusal opens with, read by the command shim to treat the journal on its port as none
PROJECT_REFUSAL_PREFIX = "__journal_wrong_project"
# Misdirected Request: the request reached a server that does not serve what it names
MISDIRECTED_STATUS = 421


class ProjectCheck:
    """Whether a request names a project other than the one this journal serves, as a launcher, shim or hook that found this journal on the port its own stale port file names would; a request naming none is from a client before the header and goes through."""

    def __init__(self, config: Config) -> None:
        self.root = config.root.resolve()

    def is_other(self, headers: dict) -> bool:
        project = headers.get(PROJECT_HEADER.lower(), "")
        return bool(project) and Path(project).resolve() != self.root

    def refusal(self, headers: dict) -> Response:
        return Response(MISDIRECTED_STATUS, {"error": f"{PROJECT_REFUSAL_PREFIX}: this is the journal of {self.root}, not of {headers.get(PROJECT_HEADER.lower())}"})
