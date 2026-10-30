from threading import get_ident

from journal.models.model import Model


class CreationCapture:
    """Rows created synchronously during one command."""

    def __init__(self) -> None:
        self._rows: list[Model] = []
        self._owner = get_ident()
        self._open = True

    def record(self, row: Model) -> None:
        if self._open and get_ident() == self._owner:
            self._rows.append(row)

    def close(self) -> list[Model]:
        self._open = False
        return self._rows.copy()
