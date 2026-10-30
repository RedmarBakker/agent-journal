from journal.features.dumps.dumps_nudges import DumpsNudges
from journal.features.dumps.states.sorting_dump import SortingDump
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.dump_with_a_file import DumpWithAFile


@story(DumpWithAFile, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_dump_holds_the_stop_is_filed_item_by_item_into_a_collection_of_its_own_and_closes_itself(story):
    dump = story.newest("dumps")
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, DumpsNudges.DUMP_OPEN_REMINDER, n=dump)
    document = story.agent_writes_a_document(story.agents.subject, "Ideas", "the ideas, sorted", "## Ideas\nThe ideas, sorted.")
    story.agent_runs(story.agents.subject, f"dump note {dump} text 'a list of ideas'")
    result = story.agent_runs(story.agents.subject, f"dump filed {dump} text 'made a doc' --refs doc:{document}")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, f"dump filed {dump} a.txt x --refs docs:99")
    result.expect_command_refused()
    result = story.agent_runs(story.agents.subject, f"dump failed {dump} a.txt unreadable")
    result.expect_command_text("closed: 1 filed, 1 failed")
    story.agent_runs(story.agents.subject, f"dump name {dump} 'Ideas for the parser'")
    result = story.agent_runs(story.agents.subject, "collection list")
    result.expect_command_text("Ideas for the parser")
    story.expect_stack(story.agents.subject, Ready, SortingDump, FollowingSequence)
