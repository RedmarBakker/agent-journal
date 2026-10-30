from journal.models.sprint_commitment import SprintCommitment
from journal.repositories.scoped_repository import ScopedRepository


class SprintCommitments(ScopedRepository[SprintCommitment]):
    model = SprintCommitment
