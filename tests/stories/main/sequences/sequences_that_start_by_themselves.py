from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

FIRST_STEP = 1


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_users_phrase_starts_its_sequence_and_the_same_phrase_again_starts_no_second_run(story):
    result = story.agent_is_prompted(story.agents.subject, "give me an update")
    result.expect_agent_told(story.agents.subject, SequencesNudges.PENDING_STEP, step=FIRST_STEP)
    story.agent_is_prompted(story.agents.subject, "give me an update")
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)
