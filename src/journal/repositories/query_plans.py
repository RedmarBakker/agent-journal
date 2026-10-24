from journal.db.connection import Connection
from journal.support.query_times import QueryTime


class QueryPlans:
    """How SQLite runs a statement the connection timed: each step of its query plan, and the steps that read a whole table or sort in a temporary tree."""

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def steps(self, query: QueryTime) -> list[str]:
        return self.connection.plan(query.sql, query.params)

    @staticmethod
    def slow_steps(steps: list[str]) -> list[str]:
        return [step for step in steps if step.startswith("SCAN ") and " USING " not in step or "TEMP B-TREE" in step]
