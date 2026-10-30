from tests.stories.fixtures.fixture_rows import FixtureRows
from tests.stories.fixtures.state_fixture import StateFixture
from journal.repositories.scope import Scope
from journal.repositories.task_outcomes import TaskOutcomes


class StoryRows:
    """The rows a story's fixture made, read by their kind and name: story.tasks.started, story.plans.first, story.messages.second; the helpers it made are read from story.agents."""

    fixture: StateFixture

    @property
    def tasks(self) -> FixtureRows:
        return self.fixture.tasks

    @property
    def plans(self) -> FixtureRows:
        return self.fixture.plans

    @property
    def messages(self) -> FixtureRows:
        return self.fixture.messages

    @property
    def checks(self) -> FixtureRows:
        return self.fixture.checks

    @property
    def sequences(self) -> FixtureRows:
        return self.fixture.sequences

    @property
    def plugins(self) -> FixtureRows:
        return self.fixture.plugins

    @property
    def aliases(self) -> FixtureRows:
        return self.fixture.aliases

    @property
    def documents(self) -> FixtureRows:
        return self.fixture.documents

    @property
    def readers(self) -> FixtureRows:
        return self.fixture.readers

    @property
    def outputs(self) -> FixtureRows:
        return self.fixture.outputs

    @property
    def memories(self) -> FixtureRows:
        return self.fixture.memories

    def expect_task_outcome_kinds(self, task_id: int, *expected: str) -> None:
        with self.app.container.get(Scope).environment(1):
            kinds = [row.kind for row in self.app.container.get(TaskOutcomes).facts(int(task_id))]
        position = 0
        for kind in kinds:
            if position < len(expected) and kind == expected[position]:
                position += 1
        assert position == len(expected), f"task {task_id} outcome history is {kinds}, not the ordered facts {expected}"

    def expect_task_outcome_summary(self, task_id: int, **expected) -> None:
        with self.app.container.get(Scope).environment(1):
            summary = self.app.container.get(TaskOutcomes).summary(int(task_id))
        fields = {name: summary.get(name) for name in expected}
        assert fields == expected, f"task {task_id} outcome summary contains {fields}, not {expected}"

    def expect_task_outcome_fact(self, task_id: int, kind: str, field: str) -> None:
        with self.app.container.get(Scope).environment(1):
            facts = self.app.container.get(TaskOutcomes).facts(int(task_id))
        fact = next((row for row in facts if row.kind == kind), None)
        value = getattr(fact, field, None) if fact else None
        assert value not in (None, ""), f"task {task_id} has no {kind} fact with {field}: {facts}"
