class FixtureRows:
    """The rows of one kind a fixture made, each read by its name, such as tasks.started: the names its own steps set, beside those it took from the fixture it builds on, and the names a story read, asked at the end whether the story used every row its fixture set."""

    def __init__(self, kind: str) -> None:
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "values", {})
        object.__setattr__(self, "own", set())
        object.__setattr__(self, "used", set())

    def __setattr__(self, name: str, value: object) -> None:
        self.own.add(name)
        self.values[name] = value

    def __getattr__(self, name: str) -> object:
        if name not in self.values:
            raise AttributeError(f"the fixture made no {self.kind} row named {name}: it has {', '.join(sorted(self.values)) or 'none'}")
        self.used.add(name)
        return self.values[name]

    def row(self, name: str, missing: object) -> object:
        return getattr(self, name) if name in self.values else missing

    def inherits(self, parent: "FixtureRows") -> None:
        self.values.update(parent.values)

    def copied(self) -> "FixtureRows":
        copy = FixtureRows(self.kind)
        copy.inherits(self)
        copy.own.update(self.own)
        return copy

    def unused(self) -> list[str]:
        return [f"{self.kind}.{name}" for name in sorted(self.own - self.used)]
