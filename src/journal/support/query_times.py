import threading
from dataclasses import dataclass

STATEMENT_CAPACITY = 500


@dataclass(frozen=True)
class QueryTime:
    """One SQL statement's runs since the last reset: how many, their total and slowest milliseconds, and the parameters of its last run."""

    sql: str
    runs: int
    total_ms: float
    slowest_ms: float
    params: tuple

    def line(self) -> str:
        return f"{self.total_ms:>8.0f} ms total  {self.total_ms / self.runs:>6.1f} ms average  {self.slowest_ms:>6.0f} ms slowest  {self.runs:>6} runs  {' '.join(self.sql.split())}"


class QueryTimes:
    """The time every SQL statement the connection runs takes, by its text, kept in memory for journal developer queries."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.statements: dict[str, QueryTime] = {}

    def add(self, sql: str, params: tuple, seconds: float) -> None:
        milliseconds = seconds * 1000
        with self.lock:
            statement = self.statements.get(sql)
            if statement is None and len(self.statements) >= STATEMENT_CAPACITY:
                return
            if statement is None:
                statement = QueryTime(sql, 0, 0.0, 0.0, params)
            self.statements[sql] = QueryTime(sql, statement.runs + 1, statement.total_ms + milliseconds, max(statement.slowest_ms, milliseconds), params)

    def slowest(self, count: int) -> list[QueryTime]:
        with self.lock:
            return sorted(self.statements.values(), key=lambda query: query.total_ms, reverse=True)[:count]

    def clear(self) -> None:
        with self.lock:
            self.statements = {}
