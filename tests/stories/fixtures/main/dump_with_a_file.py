from journal.features.dumps.states.sorting_dump import SortingDump
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class DumpWithAFile(StateFixture):
    """The user started a dump of some ideas and dropped the file a.txt in it, so the agent sorts it; the story reads the dump as story.newest("dumps")."""

    stack = (Ready, SortingDump)

    parent = WorkingAgent

    def steps(self, story) -> None:
        dump = story.user_starts_a_dump("some ideas")
        story.user_drops_a_file_in_the_dump(dump, "a.txt", b"hello")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready, SortingDump)
