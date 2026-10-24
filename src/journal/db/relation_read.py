class RelationRead(RuntimeError):
    """A list of one table's rows was being built and a query read the rows of another table: an index lists its own rows and reads no relationship."""

    def __init__(self, listed: str, table: str) -> None:
        super().__init__(f"the {listed} list read rows of {table}: an index lists its own rows alone, and a relationship is read with the rows asked for by id")
        self.listed, self.table = listed, table
