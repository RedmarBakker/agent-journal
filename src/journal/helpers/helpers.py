from typing import ClassVar

from journal.helpers.helper import Helper
from journal.helpers.researcher_helper import ResearcherHelper
from journal.helpers.reviewer_helper import ReviewerHelper
from journal.helpers.verifier_helper import VerifierHelper
from journal.helpers.worker_helper import WorkerHelper


class Helpers:
    """Every helper's file, the one list the registry is given at boot."""

    ALL: ClassVar[tuple[type[Helper], ...]] = (WorkerHelper, ReviewerHelper, VerifierHelper, ResearcherHelper)
