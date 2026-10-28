from journal.support.option import Option

# the fields a fixture keeps about its own rows, which are no rows themselves
BOOKKEEPING = ("own_rows", "rows_used")


class StateFixture:
    """A state a story starts from, reached by its seeder through the real hooks and commands, never written by hand, and checked once reached: a seeder that cannot reach it fails the story there, naming the fixture. Its fields are the rows it made, read by the story as start.<row>, the rows of the fixture it builds on with them; it names the stack it leaves the agent on, bottom first, a story's end unless the story names another, and the settings the user sets before its steps, each of which the journal must read while it is seeded."""

    parent: "type[StateFixture] | None" = None
    stack: tuple[type, ...] = ()
    settings: tuple[tuple[Option, object], ...] = ()

    def __init__(self) -> None:
        object.__setattr__(self, "own_rows", set())
        object.__setattr__(self, "rows_used", set())

    def __setattr__(self, name: str, value: object) -> None:
        self.own_rows.add(name)
        object.__setattr__(self, name, value)

    def __getattribute__(self, name: str) -> object:
        fields = object.__getattribute__(self, "__dict__")
        if name in fields and name not in BOOKKEEPING:
            fields["rows_used"].add(name)
        return object.__getattribute__(self, name)

    def rows(self) -> dict[str, object]:
        return {name: value for name, value in object.__getattribute__(self, "__dict__").items() if name not in BOOKKEEPING}

    def inherits(self, parent: "StateFixture") -> None:
        for name, value in parent.rows().items():
            object.__setattr__(self, name, value)

    def copied(self) -> "StateFixture":
        copy = type(self)()
        copy.inherits(self)
        copy.own_rows.update(self.own_rows)
        return copy

    def unused_rows(self) -> list[str]:
        return sorted(self.own_rows - self.rows_used)

    def steps(self, story) -> None:
        raise NotImplementedError

    def expected(self, story) -> None:
        raise NotImplementedError
