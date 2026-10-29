from journal.engine.states.void import Void
from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_sequence_step_that_holds_the_main_agents_writes_never_holds_the_subagent(story):
    story.agent_runs(story.agents.main, "sequence create 'release' --steps 'raise the version | push the tag'")
    sequence = story.created_number("sequence")
    story.agent_runs(story.agents.main, f"sequence run {sequence}")
    story.agent_writes(story.agents.main, "version.py")
    story.expect_refused(story.agents.main, SequencesNudges.STEP_EDIT_BLOCK, n=sequence)
    story.agent_writes(story.agents.subject, "notes.md")
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Void, Researching)
