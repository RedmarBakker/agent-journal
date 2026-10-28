from tests.scenarios.builder.fixture_copy import FixtureCopy


class FixtureCopies:
    """Each state fixture of a module's journal seeded once per provider and kept as a copy: a story starts from the copy, and a fixture that builds on another is seeded from that one's copy, so a story's setup never grows with its fixture chain."""

    def __init__(self) -> None:
        self.copies: dict[tuple[type, str], FixtureCopy] = {}

    def reached(self, scenario, fixture: type) -> None:
        copy = self.copies.get((fixture, scenario.provider))
        if copy is not None:
            copy.put_back(scenario)
            return
        self.seeded(scenario, fixture)

    def seeded(self, scenario, fixture: type) -> None:
        if fixture.builds_on is not None:
            self.reached(scenario, fixture.builds_on)
        fixture().steps(scenario)
        fixture().expected(scenario)
        self.copies[(fixture, scenario.provider)] = FixtureCopy.taken(scenario)
