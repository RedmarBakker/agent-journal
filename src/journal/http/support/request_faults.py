import threading

# how many requests in a row may fail before the journal reports itself unwell, so the supervisor starts it again
FAILING_REQUEST_COUNT = 5


class RequestFaults:
    """The requests that failed in a row, any of them raising before or while it was answered; one answered well ends the streak. A streak past FAILING_REQUEST_COUNT is a journal that answers nothing well, as a server running old code on a database newer code migrated, and its health says so."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.streak = 0
        self.last_fault = ""

    def failed(self, fault: BaseException) -> None:
        with self.lock:
            self.streak += 1
            self.last_fault = f"{type(fault).__name__}: {fault}"

    def answered(self) -> None:
        with self.lock:
            self.streak = 0

    def is_failing(self) -> bool:
        return self.streak >= FAILING_REQUEST_COUNT
