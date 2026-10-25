from journal.db.query import Query


class KeywordRows:
    """What facts, rules and reminders share: the ones the agent's words can bring up, with keywords and not kept in its context, read alone."""

    def keyword_rows(self) -> list:
        return self.newest(self.memory_query().filter_unlisted("keywords", [()]).filter(presence=False))

    def memory_query(self) -> Query:
        return self.query()
