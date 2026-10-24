class Shelf:
    """A sample for unused-page-size: the first read ignores its limit, the second passes it on."""

    def __init__(self, rows: list[str]) -> None:
        self.rows = rows

    def newest(self, limit: int) -> list[str]:
        return list(reversed(self.rows))

    def newest_page(self, limit: int) -> list[str]:
        return list(reversed(self.rows))[:limit]
