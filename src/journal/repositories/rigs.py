from journal.models.rig import Rig
from journal.repositories.scoped_repository import ScopedRepository


class Rigs(ScopedRepository[Rig]):
    model = Rig
