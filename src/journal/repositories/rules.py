from journal.models.rule import Rule
from journal.repositories.keyword_rows import KeywordRows
from journal.repositories.repository import Repository


class Rules(Repository[Rule], KeywordRows):
    model = Rule
