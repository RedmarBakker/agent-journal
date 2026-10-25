from journal.models.phase import Phase
from journal.repositories.scoped_repository import ScopedRepository

PHASE_TASK_LINK = "phase_of"


class Phases(ScopedRepository[Phase]):
    model = Phase
    member_links = (PHASE_TASK_LINK,)
