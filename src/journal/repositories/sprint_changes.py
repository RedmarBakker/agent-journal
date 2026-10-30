from journal.models.sprint_change import SprintChange
from journal.repositories.scoped_repository import ScopedRepository


class SprintChanges(ScopedRepository[SprintChange]):
    model = SprintChange
