from journal.support.option import Option
from tests.stories.fixtures.fixture_rows import FixtureRows

ROW_KINDS = ("tasks", "plans", "messages", "sequences", "plugins", "aliases", "documents", "readers", "outputs", "memories", "workers", "reviewers", "verifiers", "subagents")


class StateFixture:
    """A state a story starts from, reached by its seeder through the real hooks and commands, never written by hand, and checked once reached: a seeder that cannot reach it fails the story there, naming the fixture. The rows it made are kept by kind, self.tasks.started or self.plans.first, beside the rows of the fixture it builds on, and a story reads them as story.tasks.started, its helpers as story.agents.workers.first(); it names the stack it leaves the agent on, bottom first, a story's end unless the story names another, and the settings the user sets before its steps, each of which the journal must read while it is seeded."""

    parent: "type[StateFixture] | None" = None
    stack: tuple[type, ...] = ()
    settings: tuple[tuple[Option, object], ...] = ()

    def __init__(self) -> None:
        for kind in ROW_KINDS:
            setattr(self, kind, FixtureRows(kind))

    def kinds(self) -> list[FixtureRows]:
        return [getattr(self, kind) for kind in ROW_KINDS]

    def inherits(self, parent: "StateFixture") -> None:
        for rows, parent_rows in zip(self.kinds(), parent.kinds()):
            rows.inherits(parent_rows)

    def copied(self) -> "StateFixture":
        copy = type(self)()
        for kind in ROW_KINDS:
            setattr(copy, kind, getattr(self, kind).copied())
        return copy

    def unused_rows(self) -> list[str]:
        return [name for rows in self.kinds() for name in rows.unused()]

    def steps(self, story) -> None:
        raise NotImplementedError

    def expected(self, story) -> None:
        raise NotImplementedError
