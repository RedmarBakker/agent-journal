class StateFixture:
    """A state a scenario starts from, reached by its seeder through the real hooks and commands, never written by hand, and checked once reached: a seeder that cannot reach it fails the scenario there, naming the fixture."""

    builds_on: "type[StateFixture] | None" = None

    def seed(self, scenario) -> None:
        if self.builds_on is not None:
            self.builds_on().seed(scenario)
        self.steps(scenario)
        self.expected(scenario)

    def steps(self, scenario) -> None:
        raise NotImplementedError

    def expected(self, scenario) -> None:
        raise NotImplementedError
