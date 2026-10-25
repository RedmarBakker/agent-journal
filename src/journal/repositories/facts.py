from journal.models.fact import Fact
from journal.repositories.keyword_rows import KeywordRows
from journal.repositories.scoped_repository import ScopedRepository


class Facts(ScopedRepository[Fact], KeywordRows):
    model = Fact
