from journal.engine.states.void import Void
from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.SUBAGENT)
def test_a_sequence_step_that_holds_the_main_agents_writes_never_holds_the_subagent(story):
    story.main_agent_runs("sequence create 'release' --steps 'raise the version | push the tag'")
    sequence = story.created_number("sequence")
    story.main_agent_runs(f"sequence run {sequence}")
    story.main_agent_writes("version.py")
    story.expect_main_refused(SequencesNudges.STEP_EDIT_BLOCK, n=sequence)
    story.agent_writes("notes.md")
    story.expect_allowed()
    story.expect_stack(Void, Researching)
