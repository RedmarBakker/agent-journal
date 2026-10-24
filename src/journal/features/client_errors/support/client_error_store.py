import threading

from journal.features.client_errors.support.client_error import ClientError

ERROR_COUNT_LIMIT = 100


class ClientErrorStore:
    """The viewer's console errors in the server's memory, the same error counted and never kept twice, the oldest dropped past a hundred distinct ones."""

    def __init__(self) -> None:
        self.errors: dict[str, ClientError] = {}
        self.lock = threading.Lock()

    def add(self, message: str, stack: str) -> bool:
        key = f"{message}\n{stack}"
        with self.lock:
            existing = self.errors.get(key)
            self.errors[key] = existing.repeated() if existing else ClientError(message, stack)
            if existing is None and len(self.errors) > ERROR_COUNT_LIMIT:
                del self.errors[next(iter(self.errors))]
            return existing is None

    def all(self) -> list[ClientError]:
        with self.lock:
            return list(self.errors.values())

    def count(self) -> int:
        return len(self.errors)

    def clear(self) -> None:
        with self.lock:
            self.errors.clear()
