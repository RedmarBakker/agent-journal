class StateFixture:
    """A state a scenario starts from, reached by its seeder through the real hooks and commands, never written by hand, and checked once reached: a seeder that cannot reach it fails the scenario there, naming the fixture; it names the stack it leaves the agent on, a story's end unless the story names another."""

    builds_on: "type[StateFixture] | None" = None
    stack: tuple[str, ...] = ()

    def steps(self, scenario) -> None:
        raise NotImplementedError

    def expected(self, scenario) -> None:
        raise NotImplementedError
